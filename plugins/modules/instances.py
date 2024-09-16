#!/usr/bin/python

# Copyright: (c) 2024, Gebz gebz97@proton.me
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: instances

short_description: Lists running Oracle databases on a server.

version_added: "1.0.0"

description: This module lists all currently running Oracle databases on a server by searching for Oracle instance processes.

options: {}

author:
    - Gebz (@gebz97)
'''

EXAMPLES = r'''
# List running Oracle databases
- name: Get list of running Oracle databases
  oracle_db_list:
'''

RETURN = r'''
databases:
    description: A list of currently running Oracle databases.
    type: list
    returned: always
    sample: ['DB1', 'DB2', 'DB3']
msg:
    description: Message indicating the result of the module execution.
    type: str
    returned: on failure
    sample: 'No running Oracle databases found'
'''

from ansible.module_utils.basic import AnsibleModule
import subprocess
import re

def get_running_oracle_dbs():
    ps_command = "ps -ef | grep pmon | grep -v grep"
    try:
        ps_output = subprocess.check_output(ps_command, shell=True, universal_newlines=True).strip()
        running_dbs = re.findall(r'ora_pmon_(\w+)', ps_output)
        return running_dbs if running_dbs else []
    except subprocess.CalledProcessError:
        return []

def run_module():
    module_args = dict()

    result = dict(
        changed=False,
        databases=[]
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    running_dbs = get_running_oracle_dbs()

    if running_dbs:
        result['databases'] = running_dbs
    else:
        result['msg'] = 'No running Oracle databases found'

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
