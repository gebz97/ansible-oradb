#!/usr/bin/python

# Copyright: (c) 2024, Gebz gebz97@proton.me
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: schema

short_description: Manage Oracle database schemas

version_added: "1.0.0"

description: This module allows you to create, modify, and delete Oracle database schemas.

options:
    schema:
        description: Name of the schema to manage.
        required: true
        type: str
    password:
        description: Password for the schema.
        required: false
        type: str
    tablespace:
        description: Default tablespace for the schema.
        required: false
        type: str
    temp_tablespace:
        description: Temporary tablespace for the schema.
        required: false
        type: str
    state:
        description:
            - Desired state of the schema (present or absent).
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
    port:
        description: The port of the Oracle database.
        required: false
        type: int
        default: 1521
        
author:
    - Gebz (@gebz97)
'''

EXAMPLES = r'''
# Create a new schema
- name: Create a schema with default tablespace
  my_namespace.oracle_schema:
    schema: my_schema
    password: MyStrongPassword!
    tablespace: users
    temp_tablespace: temp
    service_name: ORCL

# Delete a schema
- name: Delete a schema
  my_namespace.oracle_schema:
    schema: my_schema
    state: absent
    service_name: ORCL
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


def schema_exists(module, sid, service_name, schema):
    """Check if the Oracle schema already exists."""
    sql = f"SELECT username FROM dba_users WHERE username = UPPER('{schema}');"
    output = execute_sqlplus(module, sql, sid, service_name)
    return schema.upper() in output


def create_schema(module, sid, service_name, schema, password, tablespace, temp_tablespace):
    """Create the Oracle schema if it doesn't exist."""
    sql = f"CREATE USER {schema} IDENTIFIED BY {password}"
    if tablespace:
        sql += f" DEFAULT TABLESPACE {tablespace}"
    if temp_tablespace:
        sql += f" TEMPORARY TABLESPACE {temp_tablespace}"
    sql += "; GRANT CONNECT, RESOURCE TO {schema};"
    execute_sqlplus(module, sql, sid, service_name)


def drop_schema(module, sid, service_name, schema):
    """Drop the Oracle schema if it exists."""
    sql = f"DROP USER {schema} CASCADE;"
    execute_sqlplus(module, sql, sid, service_name)


def run_module():
    module_args = dict(
        schema=dict(type='str', required=True),
        password=dict(type='str', required=False, no_log=True),
        tablespace=dict(type='str', required=False),
        temp_tablespace=dict(type='str', required=False),
        state=dict(type='str', required=False, default='present', choices=['present', 'absent']),
        service_name=dict(type='str', required=False),
        sid=dict(type='str', required=False),
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

    schema = module.params['schema']
    password = module.params['password']
    tablespace = module.params['tablespace']
    temp_tablespace = module.params['temp_tablespace']
    state = module.params['state']
    service_name = module.params['service_name']
    sid = module.params['sid']

    if module.check_mode:
        module.exit_json(**result)

    # Ensure we can run as the oracle user
    check_oracle_user(module)

    try:
        if state == 'present':
            if schema_exists(module, sid, service_name, schema):
                result['msg'] = f"Schema {schema} already exists on the database."
            else:
                create_schema(module, sid, service_name, schema, password, tablespace, temp_tablespace)
                result['changed'] = True
                result['msg'] = f"Schema {schema} has been created on the database."
        elif state == 'absent':
            if schema_exists(module, sid, service_name, schema):
                drop_schema(module, sid, service_name, schema)
                result['changed'] = True
                result['msg'] = f"Schema {schema} has been removed from the database."
            else:
                result['msg'] = f"Schema {schema} does not exist on the database."
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
