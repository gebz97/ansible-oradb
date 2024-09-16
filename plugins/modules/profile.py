#!/usr/bin/python

# Copyright: (c) 2024, Gebz gebz97@proton.me
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: profile

short_description: Manage Oracle database profiles

version_added: "1.0.0"

description: This module allows you to create, modify, and delete Oracle database profiles.

options:
    profile:
        description: Name of the profile to manage.
        required: true
        type: str
    limits:
        description: Dictionary of resource limits for the profile.
        required: false
        type: dict
    state:
        description:
            - Desired state of the profile (present or absent).
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
# Create a new profile
- name: Create a profile with limits
  my_namespace.oracle_profile:
    profile: my_profile
    limits:
      SESSIONS_PER_USER: 10
      CPU_PER_SESSION: 10000
    service_name: ORCL

# Modify a profile by adding limits
- name: Modify profile by adding limits
  my_namespace.oracle_profile:
    profile: my_profile
    limits:
      CPU_PER_CALL: 1000
    service_name: ORCL

# Delete a profile
- name: Delete a profile
  my_namespace.oracle_profile:
    profile: my_profile
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


def profile_exists(module, sid, service_name, profile):
    """Check if the Oracle profile already exists."""
    sql = f"SELECT profile FROM dba_profiles WHERE profile = UPPER('{profile}');"
    output = execute_sqlplus(module, sql, sid, service_name)
    return profile.upper() in output


def create_profile(module, sid, service_name, profile, limits):
    """Create the Oracle profile if it doesn't exist."""
    sql = f"CREATE PROFILE {profile}"
    if limits:
        for limit, value in limits.items():
            sql += f" LIMIT {limit} {value}"
    sql += ";"
    execute_sqlplus(module, sql, sid, service_name)


def modify_profile(module, sid, service_name, profile, limits):
    """Modify the Oracle profile if it exists."""
    if limits:
        for limit, value in limits.items():
            sql = f"ALTER PROFILE {profile} LIMIT {limit} {value};"
            execute_sqlplus(module, sql, sid, service_name)


def drop_profile(module, sid, service_name, profile):
    """Drop the Oracle profile if it exists."""
    sql = f"DROP PROFILE {profile} CASCADE;"
    execute_sqlplus(module, sql, sid, service_name)


def run_module():
    module_args = dict(
        profile=dict(type='str', required=True),
        limits=dict(type='dict', required=False),
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

    profile = module.params['profile']
    limits = module.params['limits']
    state = module.params['state']
    service_name = module.params['service_name']
    sid = module.params['sid']

    if module.check_mode:
        module.exit_json(**result)

    # Ensure we can run as the oracle user
    check_oracle_user(module)

    try:
        if state == 'present':
            if profile_exists(module, sid, service_name, profile):
                modify_profile(module, sid, service_name, profile, limits)
                result['msg'] = f"Profile {profile} has been modified on the database."
            else:
                create_profile(module, sid, service_name, profile, limits)
                result['changed'] = True
                result['msg'] = f"Profile {profile} has been created on the database."
        elif state == 'absent':
            if profile_exists(module, sid, service_name, profile):
                drop_profile(module, sid, service_name, profile)
                result['changed'] = True
                result['msg'] = f"Profile {profile} has been removed from the database."
            else:
                result['msg'] = f"Profile {profile} does not exist on the database."
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
