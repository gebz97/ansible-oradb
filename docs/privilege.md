# Ansible Module: `gebz97.oradb.privilege`

## Description

This module allows you to grant and revoke Oracle database privileges to users or roles.

## Version Added

- `1.0.0`

## Options

| Parameter     | Description                                                      | Required | Type   | Choices           | Default   |
|---------------|------------------------------------------------------------------|----------|--------|-------------------|-----------|
| `grantee`     | Name of the user or role to manage privileges for.               | Yes      | `str`  | N/A               | N/A       |
| `privileges`  | List of privileges to grant or revoke.                           | Yes      | `list` | N/A               | N/A       |
| `state`       | Desired state of the privileges (`present` or `absent`).         | No       | `str`  | `present`, `absent`| `present` |
| `service_name`| The Oracle service name (SID or Service) to connect to.           | No       | `str`  | N/A               | N/A       |
| `sid`         | The Oracle SID to connect to (used if `service_name` is not provided). | No       | `str`  | N/A               | N/A       |
| `port`        | The port of the Oracle database.                                 | No       | `int`  | N/A               | `1521`    |

## Author

- Gebz (@gebz97)

## Examples

### Grant Privileges to a User

```yaml
- name: Grant privileges to a user
  gebz97.oradb.privilege:
    grantee: my_user
    privileges:
      - CREATE SESSION
      - CREATE TABLE
    service_name: ORCL
```

### Revoke Privileges from a Role

```yaml
- name: Revoke privileges from a role
  gebz97.oradb.privilege:
    grantee: my_role
    privileges:
      - CREATE VIEW
    state: absent
    service_name: ORCL
```

## Return Values

| Key       | Description                                | Type    | Returned |
|-----------|--------------------------------------------|---------|----------|
| `changed` | Whether the module made any changes.       | `bool`  | always   |
| `msg`     | Informative message regarding the outcome. | `str`   | always   |