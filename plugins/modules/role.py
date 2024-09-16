#!/usr/bin/python

# Copyright: (c) 2024, Gebz gebz97@proton.me
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: role

short_description: Manage Oracle database roles

version_added: "1.0.0"

description: This module allows you to create, modify, and delete Oracle database roles with validated parameters.

options:
    role:
        description: Name of the role to manage.
        required: true
        type: str
    password:
        description: Password for the role (if required).
        required: false
        type: str
    privileges:
        description: List of privileges to grant to the role.
        required: false
        type: list
        elements: str
    state:
        description:
            - Desired state of the role (present or absent).
        required: false
        type: str
        default: present
        choices: ['present', 'absent']
    service_name:
        description: The Oracle service name (SID or Service) to connect to.
        required: false
        type: str
    sid:
        description: The Oracle SID to connect to (used if service_name is not provided).
        required: false
        type: str
    host:
        description: The host of the Oracle database.
        required: true
        type: str
    port:
        description: The port of the Oracle database.
        required: false
        type: int
        default: 1521
        
author:
    - Gebz (@gebz97)
'''

EXAMPLES = r'''
# Create a new role
- name: Create a role with privileges
  my_namespace.oracle_role:
    role: my_role
    privileges:
      - CREATE SESSION
      - CREATE TABLE
    service_name: ORCL
    host: 192.168.1.10

# Modify a role by adding privileges
- name: Modify role by adding privileges
  my_namespace.oracle_role:
    role: my_role
    privileges:
      - CREATE VIEW
    service_name: ORCL
    host: 192.168.1.10

# Delete a role
- name: Delete a role
  my_namespace.oracle_role:
    role: my_role
    state: absent
    service_name: ORCL
    host: 192.168.1.10
'''

RETURN = r'''
changed:
    description: Whether the module made any changes.
    type: bool
    returned: always
msg:
    description: Informative message regarding the outcome.
    type: str
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
import subprocess


def check_oracle_user(module):
    """Check if the 'oracle' user exists on the system."""
    try:
        subprocess.run(['id', 'oracle'], check=True)
    except subprocess.CalledProcessError:
        module.fail_json(msg="Oracle user does not exist on the system. Ensure 'oracle' user is available.")


def execute_sqlplus(module, sql_command, sid, service_name):
    """Execute the SQL command using sqlplus."""
    connect_str = "/ as sysdba"
    target = sid if sid else service_name

    if not target:
        module.fail_json(msg="Either SID or service_name must be provided.")

    sql_command = f'echo "{sql_command}" | sqlplus -s {connect_str} @{target}'

    try:
        result = subprocess.run(sql_command, shell=True, check=True, capture_output=True, text=True)
        if "ORA-" in result.stderr or "ORA-" in result.stdout:
            module.fail_json(msg=f"Error with SQLPlus or invalid SID/Service Name: {result.stderr or result.stdout}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        module.fail_json(msg=f"Error executing SQLPlus: {e.stderr}")


def role_exists(module, sid, service_name, role):
    """Check if the Oracle role already exists."""
    sql = f"SELECT role FROM dba_roles WHERE role = UPPER('{role}');"
    output = execute_sqlplus(module, sql, sid, service_name)
    return role.upper() in output


def create_role(module, sid, service_name, role, password, privileges):
    """Create the Oracle role if it doesn't exist."""
    sql = f"CREATE ROLE {role}"
    if password:
        sql += f" IDENTIFIED BY {password}"
    sql += ";"
    execute_sqlplus(module, sql, sid, service_name)

    if privileges:
        for privilege in privileges:
            sql = f"GRANT {privilege} TO {role};"
            execute_sqlplus(module, sql, sid, service_name)


def drop_role(module, sid, service_name, role):
    """Drop the Oracle role if it exists."""
    sql = f"DROP ROLE {role};"
    execute_sqlplus(module, sql, sid, service_name)


def run_module():
    module_args = dict(
        role=dict(type='str', required=True),
        password=dict(type='str', required=False, no_log=True),
        privileges=dict(type='list', elements='str', required=False),
        state=dict(type='str', required=False, default='present', choices=['present', 'absent']),
        service_name=dict(type='str', required=False),
        sid=dict(type='str', required=False),
        host=dict(type='str', required=True),
        port=dict(type='int', required=False, default=1521),
    )

    result = dict(
        changed=False,
        msg=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    role = module.params['role']
    password = module.params['password']
    privileges = module.params['privileges']
    state = module.params['state']
    service_name = module.params['service_name']
    sid = module.params['sid']

    if module.check_mode:
        module.exit_json(**result)

    # Ensure we can run as the oracle user
    check_oracle_user(module)

    try:
        if state == 'present':
            if role_exists(module, sid, service_name, role):
                result['msg'] = f"Role {role} already exists on the database."
            else:
                create_role(module, sid, service_name, role, password, privileges)
                result['changed'] = True
                result['msg'] = f"Role {role} has been created on the database."
        elif state == 'absent':
            if role_exists(module, sid, service_name, role):
                drop_role(module, sid, service_name, role)
                result['changed'] = True
                result['msg'] = f"Role {role} has been removed from the database."
            else:
                result['msg'] = f"Role {role} does not exist on the database."
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
