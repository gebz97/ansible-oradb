#!/usr/bin/python

# Copyright: (c) 2024, Gebz gebz97@proton.me
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: shutdown

short_description: Shutdown an Oracle database instance.

version_added: "1.0.0"

description: |
    This module shuts down an Oracle database instance with various options such as immediate, normal, transactional, or abort shutdown. 

options:
    sid:
        description: The Oracle SID of the instance to shut down.
        required: true
        type: str
    mode:
        description: The shutdown mode (IMMEDIATE, NORMAL, TRANSACTIONAL, or ABORT).
        required: false
        type: str
        choices: ['IMMEDIATE', 'NORMAL', 'TRANSACTIONAL', 'ABORT']
        default: 'IMMEDIATE'
    force:
        description: Whether to force the shutdown if there are any issues.
        required: false
        type: bool
        default: false
        
author:
    - Gebz (@gebz97)
'''

EXAMPLES = r'''
# Shutdown an Oracle instance with immediate mode
- name: Shutdown Oracle instance immediately
  oracle_shutdown:
    sid: ORCL
    mode: IMMEDIATE

# Shutdown an Oracle instance normally
- name: Normal shutdown of Oracle instance
  oracle_shutdown:
    sid: ORCL
    mode: NORMAL

# Forcefully shutdown an Oracle instance with abort mode
- name: Forcefully shutdown Oracle instance
  oracle_shutdown:
    sid: ORCL
    mode: ABORT
    force: true
'''

RETURN = r'''
changed:
    description: Whether the instance was successfully shut down.
    type: bool
    returned: always
msg:
    description: The result message indicating the success or failure of the shutdown.
    type: str
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
import subprocess
import os


def check_oracle_user(module):
    """Check if the 'oracle' user exists on the system."""
    try:
        subprocess.run(['id', 'oracle'], check=True)
    except subprocess.CalledProcessError:
        module.fail_json(msg="Oracle user does not exist on the system. Ensure 'oracle' user is available.")


def set_oracle_env(module, oracle_home, sid):
    """Set Oracle environment variables."""
    os.environ['ORACLE_SID'] = sid
    if oracle_home:
        os.environ['ORACLE_HOME'] = oracle_home


def execute_sqlplus(module, sql_command):
    """Execute a SQL command using sqlplus."""
    sqlplus_cmd = "sqlplus / as sysdba"
    sql_command = f'echo "{sql_command}" | {sqlplus_cmd}'

    try:
        result = subprocess.run(sql_command, shell=True, check=True, capture_output=True, text=True)
        if "ORA-" in result.stderr or "ORA-" in result.stdout:
            module.fail_json(msg=f"Error executing SQLPlus: {result.stderr or result.stdout}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        module.fail_json(msg=f"Error executing SQLPlus: {e.stderr}")


def shutdown_instance(module, sid, mode, force):
    """Shut down an Oracle instance with the specified mode."""
    if force:
        sql_command = "SHUTDOWN ABORT;"
    else:
        sql_command = f"SHUTDOWN {mode};"

    try:
        execute_sqlplus(module, sql_command)
    except Exception as e:
        module.fail_json(msg=f"Failed to shut down the Oracle instance: {str(e)}")


def run_module():
    module_args = dict(
        sid=dict(type='str', required=True),
        mode=dict(
            type='str',
            required=False,
            choices=['IMMEDIATE', 'NORMAL', 'TRANSACTIONAL', 'ABORT'],
            default='IMMEDIATE'
            ),
        force=dict(type='bool', required=False, default=False)
    )

    result = dict(
        changed=False,
        msg=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    sid = module.params['sid']
    mode = module.params['mode']
    force = module.params['force']

    if module.check_mode:
        module.exit_json(**result)

    check_oracle_user(module)

    try:
        shutdown_instance(module, sid, mode, force)
        result['changed'] = True
        result['msg'] = f"Oracle instance {sid} shut down successfully with {mode} mode."
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
