#!/usr/bin/python

# Copyright: (c) 2024, Gebz gebz97@proton.me
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: param

short_description: Manage Oracle PFILE/SPFILE configurations

version_added: "1.0.0"

description: This module allows you to create, modify, delete, and convert Oracle PFILE and SPFILE configurations with validated parameters.

options:
    pfile:
        description: Path to the PFILE to manage.
        required: false
        type: str
    spfile:
        description: Path to the SPFILE to manage.
        required: false
        type: str
    sid:
        description: The Oracle system identifier (SID).
        required: false
        type: str
    state:
        description:
            - Desired state of the file (present or absent).
        required: false
        type: str
        default: present
        choices: ['present', 'absent']
    action:
        description:
            - Action to perform on the file (create, modify, delete, convert).
        required: true
        type: str
        choices: ['create', 'modify', 'delete', 'convert']
    parameters:
        description: Dictionary of PFILE/SPFILE parameters to manage.
        required: false
        type: dict
        
author:
    - Gebz (@gebz97)
'''

EXAMPLES = r'''
# Create a new PFILE
- name: Create a PFILE with parameters
  my_namespace.oracle_pfile_spfile:
    pfile: /u01/app/oracle/dbs/init.ora
    sid: ORCL
    action: create
    parameters:
      db_cache_size: 104857600
      sga_target: 209715200

# Modify an SPFILE
- name: Modify SPFILE with new parameters
  my_namespace.oracle_pfile_spfile:
    spfile: /u01/app/oracle/dbs/spfileORCL.ora
    action: modify
    parameters:
      processes: 300

# Delete a PFILE
- name: Delete an old PFILE
  my_namespace.oracle_pfile_spfile:
    pfile: /u01/app/oracle/dbs/init.ora
    action: delete

# Convert PFILE to SPFILE
- name: Convert PFILE to SPFILE
  my_namespace.oracle_pfile_spfile:
    pfile: /u01/app/oracle/dbs/init.ora
    spfile: /u01/app/oracle/dbs/spfileORCL.ora
    action: convert
'''

RETURN = r'''
original_message:
    description: The original parameters that were passed.
    type: dict
    returned: always
    sample: {"db_cache_size": 104857600, "sga_target": 209715200}
message:
    description: The output message indicating the result of the action.
    type: str
    returned: always
    sample: "PFILE created successfully"
changed:
    description: Indicates if the module made any changes.
    type: bool
    returned: always
    sample: true
'''

from ansible.module_utils.basic import AnsibleModule
import os

# Valid Oracle parameters
VALID_PARAMETERS = {
    'db_cache_size': int,
    'shared_pool_size': int,
    'sga_target': int,
    'pga_aggregate_target': int,
    'processes': int,
    'audit_trail': ['DB', 'OS', 'NONE'],
    'log_archive_format': str,
    'db_block_size': int,
    'db_files': int,
    'undo_management': ['AUTO', 'MANUAL'],
    'log_buffer': int,
    # Add more parameters as needed
}

def validate_parameters(module, parameters):
    """Validate PFILE/SPFILE parameters against the known valid list."""
    for param, value in parameters.items():
        if param not in VALID_PARAMETERS:
            module.fail_json(msg=f"Invalid parameter: {param}. This parameter is not recognized.")
        
        expected_type = VALID_PARAMETERS[param]
        if isinstance(expected_type, list):
            if value not in expected_type:
                module.fail_json(msg=f"Invalid value for {param}: {value}. Allowed values are: {expected_type}.")
        else:
            try:
                expected_type(value)
            except (ValueError, TypeError):
                module.fail_json(msg=f"Invalid type for {param}: {value}. Expected {expected_type.__name__}.")

def create_file(module, sid, parameters, file_type, file_name):
    """Create PFILE/SPFILE."""
    try:
        with open(file_name, 'w') as file:
            for param, value in parameters.items():
                file.write(f"{param} = {value}\n")
        module.log(f"{file_type} created at {file_name} with parameters: {parameters}")
    except PermissionError:
        module.fail_json(msg=f"Permission denied: Unable to create {file_type} at {file_name}")

def modify_file(module, file_name, parameters):
    """Modify PFILE/SPFILE."""
    try:
        if not os.path.exists(file_name):
            module.fail_json(msg=f"The file {file_name} does not exist.")
        
        lines = []
        with open(file_name, 'r') as file:
            lines = file.readlines()

        for param, value in parameters.items():
            found = False
            for idx, line in enumerate(lines):
                if line.startswith(f"{param}"):
                    lines[idx] = f"{param} = {value}\n"
                    found = True
            if not found:
                lines.append(f"{param} = {value}\n")

        with open(file_name, 'w') as file:
            file.writelines(lines)

        module.log(f"File {file_name} modified with parameters: {parameters}")
    except PermissionError:
        module.fail_json(msg=f"Permission denied: Unable to modify {file_name}")

def delete_file(module, file_name):
    """Delete PFILE/SPFILE."""
    try:
        if os.path.exists(file_name):
            os.remove(file_name)
            module.log(f"File {file_name} deleted.")
        else:
            module.fail_json(msg=f"The file {file_name} does not exist.")
    except PermissionError:
        module.fail_json(msg=f"Permission denied: Unable to delete {file_name}")

def convert_file(module, source_file, target_file, target_type):
    """Convert PFILE to SPFILE or vice versa."""
    try:
        if not os.path.exists(source_file):
            module.fail_json(msg=f"Source file {source_file} does not exist.")
        
        with open(source_file, 'r') as source, open(target_file, 'w') as target:
            for line in source:
                target.write(line)

        module.log(f"Converted {source_file} to {target_type} at {target_file}")
    except PermissionError:
        module.fail_json(msg=f"Permission denied: Unable to convert {source_file} to {target_type} at {target_file}")

def run_module():
    module_args = dict(
        pfile=dict(type='str', required=False),
        spfile=dict(type='str', required=False),
        sid=dict(type='str', required=False),
        state=dict(type='str', required=False, default='present', choices=['present', 'absent']),
        action=dict(type='str', required=True, choices=['create', 'modify', 'delete', 'convert']),
        parameters=dict(type='dict', required=False),
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    pfile = module.params['pfile']
    spfile = module.params['spfile']
    sid = module.params['sid']
    action = module.params['action']
    parameters = module.params['parameters']

    if module.check_mode:
        module.exit_json(**result)

    if action in ['create', 'modify'] and parameters:
        validate_parameters(module, parameters)

    try:
        if action == 'create':
            if pfile:
                create_file(module, sid, parameters, 'PFILE', pfile)
            if spfile:
                create_file(module, sid, parameters, 'SPFILE', spfile)
            result['changed'] = True
            result['message'] = "PFILE/SPFILE created successfully."
        elif action == 'modify':
            if pfile:
                modify_file(module, pfile, parameters)
            if spfile:
                modify_file(module, spfile, parameters)
            result['changed'] = True
            result['message'] = "PFILE/SPFILE modified successfully."
        elif action == 'delete':
            if pfile:
                delete_file(module, pfile)
            if spfile:
                delete_file(module, spfile)
            result['changed'] = True
            result['message'] = "PFILE/SPFILE deleted successfully."
        elif action == 'convert':
            if pfile and spfile:
                convert_file(module, pfile, spfile, 'SPFILE')
            elif spfile and pfile:
                convert_file(module, spfile, pfile, 'PFILE')
            result['changed'] = True
            result['message'] = "PFILE/SPFILE conversion completed."
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

    result['original_message'] = parameters
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
