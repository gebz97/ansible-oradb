#!/usr/bin/python

# Copyright: (c) 2024, Gebz gebz97@proton.me
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: tablespace

short_description: Manage Oracle database tablespaces

version_added: "1.0.0"

description: This module allows you to create, modify, and delete Oracle database tablespaces.

options:
    tablespace:
        description: Name of the tablespace to manage.
        required: true
        type: str
    datafile:
        description: Path to the datafile for the tablespace.
        required: false
        type: str
    size:
        description: Size of the tablespace (e.g., 100M, 1G).
        required: false
        type: str
    autoextend:
        description: Whether to enable autoextend for the tablespace.
        required: false
        type: bool
        default: false
    maxsize:
        description: Maximum size for the tablespace if autoextend is enabled.
        required: false
        type: str
    state:
        description:
            - Desired state of the tablespace (present or absent).
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
# Create a new tablespace
- name: Create a tablespace
  my_namespace.oracle_tablespace:
    tablespace: my_tablespace
    datafile: /u01/app/oracle/oradata/mydb/my_tablespace.dbf
    size: 100M
    autoextend: true
    maxsize: 1G
    service_name: ORCL

# Delete a tablespace
- name: Delete a tablespace
  my_namespace.oracle_tablespace:
    tablespace: my_tablespace
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


def tablespace_exists(module, sid, service_name, tablespace):
    """Check if the Oracle tablespace already exists."""
    sql = f"SELECT tablespace_name FROM dba_tablespaces WHERE tablespace_name = UPPER('{tablespace}');"
    output = execute_sqlplus(module, sql, sid, service_name)
    return tablespace.upper() in output


def create_tablespace(module, sid, service_name, tablespace, datafile, size, autoextend, maxsize):
    """Create the Oracle tablespace if it doesn't exist."""
    sql = f"CREATE TABLESPACE {tablespace} DATAFILE '{datafile}' SIZE {size}"
    if autoextend:
        sql += " AUTOEXTEND ON"
        if maxsize:
            sql += f" MAXSIZE {maxsize}"
    sql += ";"
    execute_sqlplus(module, sql, sid, service_name)


def drop_tablespace(module, sid, service_name, tablespace):
    """Drop the Oracle tablespace if it exists."""
    sql = f"DROP TABLESPACE {tablespace} INCLUDING CONTENTS AND DATAFILES;"
    execute_sqlplus(module, sql, sid, service_name)


def run_module():
    module_args = dict(
        tablespace=dict(type='str', required=True),
        datafile=dict(type='str', required=False),
        size=dict(type='str', required=False),
        autoextend=dict(type='bool', required=False, default=False),
        maxsize=dict(type='str', required=False),
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

    tablespace = module.params['tablespace']
    datafile = module.params['datafile']
    size = module.params['size']
    autoextend = module.params['autoextend']
    maxsize = module.params['maxsize']
    state = module.params['state']
    service_name = module.params['service_name']
    sid = module.params['sid']

    if module.check_mode:
        module.exit_json(**result)

    # Ensure we can run as the oracle user
    check_oracle_user(module)

    try:
        if state == 'present':
            if tablespace_exists(module, sid, service_name, tablespace):
                result['msg'] = f"Tablespace {tablespace} already exists on the database."
            else:
                create_tablespace(module, sid, service_name, tablespace, datafile, size, autoextend, maxsize)
                result['changed'] = True
                result['msg'] = f"Tablespace {tablespace} has been created on the database."
        elif state == 'absent':
            if tablespace_exists(module, sid, service_name, tablespace):
                drop_tablespace(module, sid, service_name, tablespace)
                result['changed'] = True
                result['msg'] = f"Tablespace {tablespace} has been removed from the database."
            else:
                result['msg'] = f"Tablespace {tablespace} does not exist on the database."
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
