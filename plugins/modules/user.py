#!/usr/bin/python

# Copyright: (c) 2024, Gebz97 gebz97@proton.me
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: user

short_description: Ensures a user exists on an Oracle database instance.

version_added: "1.0.0"

description: |
    This module ensures a specific user exists or is removed from an Oracle database instance. 
    It requires the use of become to elevate privileges and execute commands as the Oracle user.

options:
    username:
        description: The name of the user to ensure exists on the Oracle database.
        required: true
        type: str
    password:
        description: The password to use if the user needs to be created.
        required: true
        type: str
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
    state:
        description: Whether the user should exist or be absent.
        required: false
        type: str
        choices: ['present', 'absent']
        default: 'present'

author:
    - Gebz (@gebz97)
'''

EXAMPLES = r'''
# Ensure a user exists on an Oracle database using service name
- name: Ensure Oracle user exists
  oracle_user:
    username: testuser
    password: MyStrongPassword!
    service_name: ORCL

# Remove a user from an Oracle database
- name: Remove Oracle user
  oracle_user:
    username: testuser
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
import re


def validate_password(password):
    """Check for problematic symbols in the password based on Oracle guidelines."""
    if re.search(r'[\'";@]', password):
        raise ValueError("Password contains forbidden symbols such as quotes, semicolons, or '@'.")
    if re.search(r'^[^a-zA-Z]', password):
        raise ValueError("Password must start with an alphabetic character.")
    if re.search(r'[^\w_$#]', password):
        raise ValueError("Password contains invalid characters. Only alphanumeric, '_', '$', and '#' are allowed.")
    if re.search(r'[$#]', password):
        raise ValueError("Password contains discouraged symbols '$' or '#'.")
    # Additional checks can be added here if needed


def check_oracle_user(module):
    """Check if the 'oracle' user exists on the system."""
    try:
        # Check if oracle user exists by running 'id oracle'
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


def user_exists(module, sid, service_name, username):
    """Check if the Oracle user already exists."""
    sql = f"SELECT username FROM dba_users WHERE username = UPPER('{username}');"
    output = execute_sqlplus(module, sql, sid, service_name)
    return username.upper() in output


def create_user(module, sid, service_name, username, password):
    """Create the Oracle user if they don't exist."""
    sql = f"CREATE USER {username} IDENTIFIED BY {password}; GRANT CONNECT, RESOURCE TO {username};"
    execute_sqlplus(module, sql, sid, service_name)


def drop_user(module, sid, service_name, username):
    """Drop the Oracle user if they exist."""
    sql = f"DROP USER {username} CASCADE;"
    execute_sqlplus(module, sql, sid, service_name)


def run_module():
    module_args = dict(
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        service_name=dict(type='str', required=False),
        sid=dict(type='str', required=False),
        port=dict(type='int', required=False, default=1521),
        state=dict(type='str', required=False, choices=['present', 'absent'], default='present')
    )

    result = dict(
        changed=False,
        msg=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    username = module.params['username']
    password = module.params['password']
    service_name = module.params['service_name']
    sid = module.params['sid']
    state = module.params['state']

    if module.check_mode:
        module.exit_json(**result)

    # Ensure we can run as the oracle user
    check_oracle_user(module)

    try:
        # Validate password
        validate_password(password)

        if state == 'present':
            if user_exists(module, sid, service_name, username):
                result['msg'] = f"User {username} already exists on the database."
            else:
                create_user(module, sid, service_name, username, password)
                result['changed'] = True
                result['msg'] = f"User {username} has been created on the database."
        elif state == 'absent':
            if user_exists(module, sid, service_name, username):
                drop_user(module, sid, service_name, username)
                result['changed'] = True
                result['msg'] = f"User {username} has been removed from the database."
            else:
                result['msg'] = f"User {username} does not exist on the database."
    except ValueError as e:
        module.fail_json(msg=str(e))
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
