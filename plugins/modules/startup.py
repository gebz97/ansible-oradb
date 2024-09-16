#!/usr/bin/python

# Copyright: (c) 2024, Gebz gebz97@proton.me
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: startup

short_description: Startup an Oracle database instance.

version_added: "1.0.0"

description: |
    This module starts an Oracle database instance with optional startup modes such as restricted mode, and the ability to specify the Oracle SID.

options:
    sid:
        description: The Oracle SID of the database to start.
        required: false
        type: str
    pfile:
        description: The path to the pfile/spfile if required for startup.
        required: false
        type: str
    mode:
        description: The startup mode for the Oracle database.
        required: false
        type: str
        choices: ['normal', 'mount', 'restrict', 'force']
        default: 'normal'
    oracle_home:
        description: The ORACLE_HOME environment variable.
        required: false
        type: str
    oracle_base:
        description: The ORACLE_BASE environment variable.
        required: false
        type: str
        
author:
    - Gebz (@gebz97)
'''

EXAMPLES = r'''
# Start an Oracle database with normal startup
- name: Start Oracle database in normal mode
  oracle_db_startup:
    sid: ORCL

# Start an Oracle database in restricted mode
- name: Start Oracle database in restricted mode
  oracle_db_startup:
    sid: ORCL
    mode: restrict

# Start an Oracle database using a specific pfile
- name: Start Oracle database with pfile
  oracle_db_startup:
    sid: ORCL
    pfile: /u01/app/oracle/dbs/initORCL.ora
'''

RETURN = r'''
changed:
    description: Whether the database was started or not.
    type: bool
    returned: always
msg:
    description: Informative message regarding the outcome.
    type: str
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
import os
import subprocess


def check_oracle_user(module):
    """Check if the 'oracle' user exists on the system."""
    try:
        # Check if oracle user exists by running 'id oracle'
        subprocess.run(['id', 'oracle'], check=True)
    except subprocess.CalledProcessError:
        module.fail_json(msg="Oracle user does not exist on the system. Ensure 'oracle' user is available.")


def set_oracle_env(module, oracle_home, oracle_base, sid):
    """Set Oracle environment variables."""
    if oracle_home:
        os.environ['ORACLE_HOME'] = oracle_home
    if oracle_base:
        os.environ['ORACLE_BASE'] = oracle_base
    if sid:
        os.environ['ORACLE_SID'] = sid


def startup_db(module, sid, mode, pfile):
    """Start the Oracle database with the given parameters."""
    sqlplus_cmd = "/ as sysdba"
    startup_cmd = "STARTUP"

    if mode == 'restrict':
        startup_cmd += " RESTRICT"
    elif mode == 'mount':
        startup_cmd += " MOUNT"
    elif mode == 'force':
        startup_cmd = "STARTUP FORCE"

    if pfile:
        startup_cmd += f" PFILE='{pfile}'"

    sql_command = f'echo "{startup_cmd};" | sqlplus -s {sqlplus_cmd}'

    try:
        result = subprocess.run(sql_command, shell=True, check=True, capture_output=True, text=True)
        if "ORA-" in result.stderr or "ORA-" in result.stdout:
            module.fail_json(msg=f"Error during database startup: {result.stderr or result.stdout}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        module.fail_json(msg=f"Error executing SQLPlus for startup: {e.stderr}")


def run_module():
    module_args = dict(
        sid=dict(type='str', required=False),
        pfile=dict(type='str', required=False),
        mode=dict(type='str', required=False, choices=['normal', 'mount', 'restrict', 'force'], default='normal'),
        oracle_home=dict(type='str', required=False),
        oracle_base=dict(type='str', required=False),
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
    pfile = module.params['pfile']
    mode = module.params['mode']
    oracle_home = module.params['oracle_home']
    oracle_base = module.params['oracle_base']

    if module.check_mode:
        module.exit_json(**result)

    # Ensure we can run as the oracle user
    check_oracle_user(module)

    # Set Oracle environment variables
    set_oracle_env(module, oracle_home, oracle_base, sid)

    try:
        # Start the database
        startup_db(module, sid, mode, pfile)
        result['changed'] = True
        result['msg'] = f"Oracle database with SID {sid} started in {mode} mode."
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
