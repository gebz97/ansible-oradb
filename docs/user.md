# Ansible Module: `gebz97.oradb.user`

## Description

This module ensures a specific user exists or is removed from an Oracle database instance. It requires the use of become to elevate privileges and execute commands as the Oracle user.

## Version Added

- `1.0.0`

## Options

| Parameter    | Description                                                  | Required | Type   | Choices         | Default |
|--------------|--------------------------------------------------------------|----------|--------|-----------------|---------|
| `username`   | The name of the user to ensure exists on the Oracle database. | Yes      | `str`  | N/A             | N/A     |
| `password`   | The password to use if the user needs to be created.         | Yes      | `str`  | N/A             | N/A     |
| `service_name` | The Oracle service name (SID or Service) to connect to.     | No       | `str`  | N/A             | N/A     |
| `sid`        | The Oracle SID to connect to (used if `service_name` is not provided). | No       | `str`  | N/A             | N/A     |
| `port`       | The port of the Oracle database.                             | No       | `int`  | N/A             | `1521`  |
| `state`      | Whether the user should exist or be absent (`present` or `absent`). | No       | `str`  | `present`, `absent` | `present` |

## Author

- Gebz (@gebz97)

## Examples

### Ensure a User Exists on an Oracle Database Using Service Name

```yaml
- name: Ensure Oracle user exists
  gebz97.oradb.user:
    username: testuser
    password: MyStrongPassword!
    service_name: ORCL
```

### Remove a User from an Oracle Database

```yaml
- name: Remove Oracle user
  gebz97.oradb.user:
    username: testuser
    state: absent
    service_name: ORCL
```

## Return Values

| Key       | Description                                    | Type   | Returned |
|-----------|------------------------------------------------|--------|----------|
| `changed` | Whether the module made any changes.           | `bool` | always   |
| `msg`     | Informative message regarding the outcome.     | `str`  | always   |