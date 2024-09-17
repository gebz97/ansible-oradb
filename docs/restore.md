# Ansible Module: `gebz97.oradb.restore`

## Description

This module allows you to restore Oracle database backups using RMAN, specifying the type of restore and including optional RMAN parameters.

## Version Added

- `1.0.0`

## Options

| Parameter        | Description                                                                           | Required | Type   | Choices                | Default   |
|------------------|---------------------------------------------------------------------------------------|----------|--------|------------------------|-----------|
| `restore_type`   | Type of restore to perform (`database` or `tablespace`).                               | Yes      | `str`  | `database`, `tablespace`| N/A       |
| `name`           | Name of the tablespace to restore (required if `restore_type` is `tablespace`).        | No       | `str`  | N/A                    | N/A       |
| `rman_parameters`| Dictionary of RMAN parameters to include in the restore command.                       | No       | `dict` | N/A                    | N/A       |
| `user`           | The Oracle user to connect as.                                                         | No       | `str`  | N/A                    | N/A       |
| `password`       | The password for the Oracle user.                                                      | No       | `str`  | N/A                    | N/A       |
| `connection_type`| The connection type (e.g., `sysdba`, `sysoper`).                                       | No       | `str`  | `sysdba`, `sysoper`     | `sysdba`  |
| `service_name`   | The Oracle service name (SID or Service) to connect to.                                 | No       | `str`  | N/A                    | N/A       |
| `sid`            | The Oracle SID to connect to (used if `service_name` is not provided).                 | No       | `str`  | N/A                    | N/A       |

## Author

- Gebz (@gebz97)

## Examples

### Restore the Entire Database

```yaml
- name: Restore the entire database
  gebz97.oradb.restore:
    restore_type: database
    user: johndoe
    password: password123
    connection_type: sysdba
    service_name: ORCL
```

### Restore a Specific Tablespace

```yaml
- name: Restore a specific tablespace
  gebz97.oradb.restore:
    restore_type: tablespace
    name: my_tablespace
    user: johndoe
    password: password123
    connection_type: sysdba
    service_name: ORCL
```

### Restore with RMAN Parameters

```yaml
- name: Restore the entire database with RMAN parameters
  gebz97.oradb.restore:
    restore_type: database
    rman_parameters:
      UNTIL TIME: "SYSDATE-1"
    user: johndoe
    password: password123
    connection_type: sysdba
    service_name: ORCL
```

## Return Values

| Key       | Description                                | Type    | Returned |
|-----------|--------------------------------------------|---------|----------|
| `changed` | Whether the module made any changes.       | `bool`  | always   |
| `msg`     | Informative message regarding the outcome. | `str`   | always   |