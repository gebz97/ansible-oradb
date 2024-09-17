# Ansible Module: `gebz97.oradb.backup`

## Description

This module allows you to create backups using Oracle Recovery Manager (RMAN), specifying what to back up and including RMAN parameters.

## Requirements

- Oracle RMAN
- Oracle Database instance

## Version Added

- `1.0.0`

## Options

| Parameter         | Description                                                                                      | Required | Type   | Choices                                  | Default     |
|-------------------|--------------------------------------------------------------------------------------------------|----------|--------|------------------------------------------|-------------|
| `backup_type`     | Type of backup to perform.                                                                        | Yes      | `str`  | `database`, `archivelog`, `tablespace`   | N/A         |
| `name`            | Name of the tablespace to back up (required if `backup_type` is `tablespace`).                    | No       | `str`  | N/A                                      | N/A         |
| `rman_parameters` | Dictionary of RMAN parameters to include in the backup command.                                    | No       | `dict` | N/A                                      | N/A         |
| `user`            | The Oracle user to connect as.                                                                    | No       | `str`  | N/A                                      | N/A         |
| `password`        | The password for the Oracle user.                                                                 | No       | `str`  | N/A                                      | N/A         |
| `connection_type` | The connection type (e.g., `sysdba`, `sysoper`).                                                  | No       | `str`  | N/A                                      | `sysdba`    |
| `service_name`    | The Oracle service name (SID or Service) to connect to.                                            | No       | `str`  | N/A                                      | N/A         |
| `sid`             | The Oracle SID to connect to (used if `service_name` is not provided).                            | No       | `str`  | N/A                                      | N/A         |

## Author

- Gebz (@gebz97)

## Examples

### Backup the Entire Database

```yaml
- name: Backup the entire database
  gebz97.oradb.backup:
    backup_type: database
    user: johndoe
    password: password123
    connection_type: sysdba
    service_name: ORCL
```

### Backup Archivelogs

```yaml
- name: Backup archivelogs
  gebz97.oradb.backup:
    backup_type: archivelog
    user: johndoe
    password: password123
    connection_type: sysdba
    service_name: ORCL
```

### Backup a Specific Tablespace

```yaml
- name: Backup a specific tablespace
  gebz97.oradb.backup:
    backup_type: tablespace
    name: my_tablespace
    user: johndoe
    password: password123
    connection_type: sysdba
    service_name: ORCL
```

### Backup with RMAN Parameters

```yaml
- name: Backup the entire database with RMAN parameters
  gebz97.oradb.backup:
    backup_type: database
    rman_parameters:
      FORMAT: '/backup/DB_%U'
      TAG: 'FULL_DB_BACKUP'
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