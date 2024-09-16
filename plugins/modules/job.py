#!/usr/bin/python

# Copyright: (c) 2024, Gebz gebz97@proton.me
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: job

short_description: Manage Oracle database jobs

version_added: "1.0.0"

description: This module allows you to create, modify, and delete Oracle database jobs.

options:
    job_name:
        description: Name of the job to manage.
        required: true
        type: str
    job_action:
        description: The PL/SQL block or stored procedure to execute.
        required: false
        type: str
    schedule:
        description: The schedule for the job (e.g., 'FREQ=DAILY; BYHOUR=12; BYMINUTE=0; BYSECOND=0').
        required: false
        type: str
    state:
        description:
            - Desired state of the job (present or absent).
        required: false
        type: str
        default: present
        choices: ['present', 'absent']
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
# Create a new job
- name: Create a job
  my_namespace.oracle_job:
    job_name: my_job
    job_action: 'BEGIN my_procedure; END;'
    schedule: 'FREQ=DAILY; BYHOUR=12; BYMINUTE=0; BYSECOND=0'
    user: johndoe
    password: password123
    connection_type: sysdba
    service_name: ORCL

# Delete a job
- name: Delete a job
  my_namespace.oracle_job:
    job_name: my_job
    state: absent
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


def execute_sqlplus(module, sql_command, user, password, connection_type, sid, service_name):
    """Execute the SQL command using sqlplus."""
    target = sid if sid else service_name

    if not target:
        module.fail_json(msg="Either SID or service_name must be provided.")

    os.environ['ORACLE_SID'] = sid if sid else ''
    sql_command_file = "/tmp/sql_command_file.sql"

    with open(sql_command_file, 'w') as file:
        file.write(sql_command)

    if user and password:
        connect_str = f"{user}/{password} as {connection_type}"
    else:
        connect_str = "/ as sysdba"

    command = f"sqlplus -s {connect_str} @{sql_command_file}"

    rc, stdout, stderr = module.run_command(command)
    os.remove(sql_command_file)

    if rc != 0:
        module.fail_json(msg=f"Error executing SQLPlus: {stderr}")

    return stdout.strip()


def job_exists(module, user, password, connection_type, sid, service_name, job_name):
    """Check if the Oracle job already exists."""
    sql = f"SELECT job_name FROM dba_scheduler_jobs WHERE job_name = UPPER('{job_name}');"
    output = execute_sqlplus(module, sql, user, password, connection_type, sid, service_name)
    return job_name.upper() in output


def create_job(module, user, password, connection_type, sid, service_name, job_name, job_action, schedule):
    """Create the Oracle job if it doesn't exist."""
    sql = f"""
    BEGIN
        DBMS_SCHEDULER.create_job (
            job_name        => '{job_name}',
            job_type        => 'PLSQL_BLOCK',
            job_action      => '{job_action}',
            start_date      => SYSTIMESTAMP,
            repeat_interval => '{schedule}',
            enabled         => TRUE
        );
    END;
    """
    execute_sqlplus(module, sql, user, password, connection_type, sid, service_name)


def drop_job(module, user, password, connection_type, sid, service_name, job_name):
    """Drop the Oracle job if it exists."""
    sql = f"BEGIN DBMS_SCHEDULER.drop_job('{job_name}'); END;"
    execute_sqlplus(module, sql, user, password, connection_type, sid, service_name)


def run_module():
    module_args = dict(
        job_name=dict(type='str', required=True),
        job_action=dict(type='str', required=False),
        schedule=dict(type='str', required=False),
        state=dict(type='str', required=False, default='present', choices=['present', 'absent']),
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

    job_name = module.params['job_name']
    job_action = module.params['job_action']
    schedule = module.params['schedule']
    state = module.params['state']
    user = module.params['user']
    password = module.params['password']
    connection_type = module.params['connection_type']
    service_name = module.params['service_name']
    sid = module.params['sid']

    if module.check_mode:
        module.exit_json(**result)

    try:
        if state == 'present':
            if job_exists(module, user, password, connection_type, sid, service_name, job_name):
                result['msg'] = f"Job {job_name} already exists on the database."
            else:
                create_job(module, user, password, connection_type, sid, service_name, job_name, job_action, schedule)
                result['changed'] = True
                result['msg'] = f"Job {job_name} has been created on the database."
        elif state == 'absent':
            if job_exists(module, user, password, connection_type, sid, service_name, job_name):
                drop_job(module, user, password, connection_type, sid, service_name, job_name)
                result['changed'] = True
                result['msg'] = f"Job {job_name} has been removed from the database."
            else:
                result['msg'] = f"Job {job_name} does not exist on the database."
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
