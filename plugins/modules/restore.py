#!/usr/bin/python

# Copyright: (c) 2024, Gebz gebz97@proton.me
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: restore

short_description: Restore backups using RMAN

version_added: "1.0.0"

description: This module allows you to restore backups using RMAN, specifying what to restore and including RMAN parameters.

options:
    restore_type:
        description: Type of restore to perform (database, tablespace).
        required: true
        type: str
        choices: ['database', 'tablespace']
    name:
        description: Name of the tablespace to restore (required if restore_type is tablespace).
        required: false
        type: str
    rman_parameters:
        description: Dictionary of RMAN parameters to include in the restore command.
        required: false
        type: dict
    user:
        description: The Oracle user to connect as.
        required: false
        type: str
    password:
        description: The password for the Oracle user.
        required: false
        type: str
        no_log: true
    connection_type:
        description: The connection type (e.g., sysdba, sysoper).
        required: false
        type: str
        default: "sysdba"
    service_name:
        description: The Oracle service name (SID or Service) to connect to.
        required: false
        type: str
    sid:
        description: The Oracle SID to connect to (used if service_name is not provided).
        required: false
        type: str
        
author:
    - Gebz (@gebz97)
'''

EXAMPLES = r'''
# Restore the entire database
- name: Restore the entire database
  my_namespace.oracle_rman_restore:
    restore_type: database
    user: johndoe
    password: password123
    connection_type: sysdba
    service_name: ORCL

# Restore a specific tablespace
- name: Restore a specific tablespace
  my_namespace.oracle_rman_restore:
    restore_type: tablespace
    name: my_tablespace
    user: johndoe
    password: password123
    connection_type: sysdba
    service_name: ORCL

# Restore with RMAN parameters
- name: Restore the entire database with RMAN parameters
  my_namespace.oracle_rman_restore:
    restore_type: database
    rman_parameters:
      UNTIL TIME: "SYSDATE-1"
    user: johndoe
    password: password123
    connection_type: sysdba
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
import os
import time


def execute_rman(module, rman_command, user, password, connection_type, sid, service_name, retries=3):
    """Execute the RMAN command with retry logic."""
    target = sid if sid else service_name

    if not target:
        module.fail_json(msg="Either SID or service_name must be provided.")

    os.environ['ORACLE_SID'] = sid if sid else ''
    rman_command_file = "/tmp/rman_command_file.rman"

    with open(rman_command_file, 'w') as file:
        file.write(rman_command)

    if user and password:
        connect_str = f"{user}/{password} as {connection_type}"
    else:
        connect_str = "/ as sysdba"

    command = f"rman target '{connect_str}' cmdfile={rman_command_file}"

    attempt = 0
    while attempt < retries:
        rc, stdout, stderr = module.run_command(command)
        if rc == 0:
            os.remove(rman_command_file)
            return stdout.strip()
        else:
            attempt += 1
            time.sleep(10)  # Wait before retrying

    os.remove(rman_command_file)
    module.fail_json(msg=f"Error executing RMAN after {retries} attempts: {stderr}")




def build_rman_command(restore_type, name, rman_parameters):
    """Build the RMAN command based on the restore type and parameters."""
    command = "RESTORE"

    if restore_type == "database":
        command += " DATABASE"
    elif restore_type == "tablespace":
        command += f" TABLESPACE {name}"

    if rman_parameters:
        for param, value in rman_parameters.items():
            command += f" {param} {value}"

    return command


def validate_parameters(module, restore_type, name):
    """Validate the parameters based on the restore type."""
    if restore_type == "tablespace" and not name:
        module.fail_json(msg="The 'name' parameter is required when restore_type is 'tablespace'.")


def run_module():
    module_args = dict(
        restore_type=dict(type='str', required=True, choices=['database', 'tablespace']),
        name=dict(type='str', required=False),
        rman_parameters=dict(type='dict', required=False),
        user=dict(type='str', required=False),
        password=dict(type='str', required=False, no_log=True),
        connection_type=dict(type='str', required=False, default="sysdba"),
        service_name=dict(type='str', required=False),
        sid=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        msg=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    restore_type = module.params['restore_type']
    name = module.params['name']
    rman_parameters = module.params['rman_parameters']
    user = module.params['user']
    password = module.params['password']
    connection_type = module.params['connection_type']
    service_name = module.params['service_name']
    sid = module.params['sid']

    if module.check_mode:
        module.exit_json(**result)

    # Validate parameters
    validate_parameters(module, restore_type, name)

    try:
        rman_command = build_rman_command(restore_type, name, rman_parameters)
        execute_rman(module, rman_command, user, password, connection_type, sid, service_name)
        result['changed'] = True
        result['msg'] = f"RMAN restore of type {restore_type} has been completed."
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
