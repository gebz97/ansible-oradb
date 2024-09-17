# Ansible Module: `gebz97.oradb.job`

## Description

This module allows you to create, modify, and delete Oracle database jobs.

## Version Added

- `1.0.0`

## Options

| Parameter         | Description                                                                                       | Required | Type   | Choices              | Default     |
|-------------------|---------------------------------------------------------------------------------------------------|----------|--------|----------------------|-------------|
| `job_name`        | Name of the job to manage.                                                                         | Yes      | `str`  | N/A                  | N/A         |
| `job_action`      | The PL/SQL block or stored procedure to execute.                                                   | No       | `str`  | N/A                  | N/A         |
| `schedule`        | The schedule for the job (e.g., `FREQ=DAILY; BYHOUR=12; BYMINUTE=0; BYSECOND=0`).                  | No       | `str`  | N/A                  | N/A         |
| `state`           | Desired state of the job (`present` or `absent`).                                                  | No       | `str`  | `present`, `absent`   | `present`   |
| `user`            | The Oracle user to connect as.                                                                     | No       | `str`  | N/A                  | N/A         |
| `password`        | The password for the Oracle user.                                                                  | No       | `str`  | N/A                  | N/A         |
| `connection_type` | The connection type (e.g., `sysdba`, `sysoper`).                                                   | No       | `str`  | N/A                  | `sysdba`    |
| `service_name`    | The Oracle service name (SID or Service) to connect to.                                             | No       | `str`  | N/A                  | N/A         |
| `sid`             | The Oracle SID to connect to (used if `service_name` is not provided).                             | No       | `str`  | N/A                  | N/A         |

## Author

- Gebz (@gebz97)

## Examples

### Create a New Job

```yaml
- name: Create a job
  gebz97.oradb.job:
    job_name: my_job
    job_action: 'BEGIN my_procedure; END;'
    schedule: 'FREQ=DAILY; BYHOUR=12; BYMINUTE=0; BYSECOND=0'
    user: johndoe
    password: password123
    connection_type: sysdba
    service_name: ORCL
```

### Delete a Job

```yaml
- name: Delete a job
  gebz97.oradb.job:
    job_name: my_job
    state: absent
    user: johndoe
    password: password123
    connection_type: sysdba
    service_name: ORCL
```

## Return Values

| Key      | Description                                | Type    | Returned |
|----------|--------------------------------------------|---------|----------|
| `changed`| Whether the module made any changes.       | `bool`  | always   |
| `msg`    | Informative message regarding the outcome. | `str`   | always   |