# Ansible Module: `gebz97.oradb.role`

## Description

This module allows you to manage Oracle database roles, including creating, modifying, and deleting roles, with support for granting privileges.

## Version Added

- `1.0.0`

## Options

| Parameter        | Description                                                        | Required | Type     | Choices                | Default   |
|------------------|--------------------------------------------------------------------|----------|----------|------------------------|-----------|
| `role`           | Name of the role to manage.                                        | Yes      | `str`    | N/A                    | N/A       |
| `password`       | Password for the role (if required).                               | No       | `str`    | N/A                    | N/A       |
| `privileges`     | List of privileges to grant to the role.                           | No       | `list`   | N/A                    | N/A       |
| `state`          | Desired state of the role (`present` or `absent`).                 | No       | `str`    | `present`, `absent`     | `present` |
| `service_name`   | The Oracle service name (SID or Service) to connect to.            | No       | `str`    | N/A                    | N/A       |
| `sid`            | The Oracle SID to connect to (used if `service_name` is not set).  | No       | `str`    | N/A                    | N/A       |
| `port`           | The port of the Oracle database.                                   | No       | `int`    | N/A                    | `1521`    |

## Author

- Gebz (@gebz97)

## Examples

### Create a New Role with Privileges

```yaml
- name: Create a role with privileges
  gebz97.oradb.role:
    role: my_role
    privileges:
      - CREATE SESSION
      - CREATE TABLE
    service_name: ORCL
```

### Modify a Role by Adding Privileges

```yaml
- name: Modify role by adding privileges
  gebz97.oradb.role:
    role: my_role
    privileges:
      - CREATE VIEW
    service_name: ORCL
```

### Delete a Role

```yaml
- name: Delete a role
  gebz97.oradb.role:
    role: my_role
    state: absent
    service_name: ORCL
```

## Return Values

| Key       | Description                                | Type    | Returned |
|-----------|--------------------------------------------|---------|----------|
| `changed` | Whether the module made any changes.       | `bool`  | always   |
| `msg`     | Informative message regarding the outcome. | `str`   | always   |