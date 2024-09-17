# Ansible Module: `gebz97.oradb.tablespace`

## Description

This module allows you to create, modify, and delete Oracle database tablespaces.

## Version Added

- `1.0.0`

## Options

| Parameter    | Description                                                  | Required | Type   | Choices           | Default |
|--------------|--------------------------------------------------------------|----------|--------|-------------------|---------|
| `tablespace` | Name of the tablespace to manage.                            | Yes      | `str`  | N/A               | N/A     |
| `datafile`   | Path to the datafile for the tablespace.                     | No       | `str`  | N/A               | N/A     |
| `size`       | Size of the tablespace (e.g., 100M, 1G).                     | No       | `str`  | N/A               | N/A     |
| `autoextend` | Whether to enable autoextend for the tablespace.             | No       | `bool` | N/A               | `false` |
| `maxsize`    | Maximum size for the tablespace if autoextend is enabled.    | No       | `str`  | N/A               | N/A     |
| `state`      | Desired state of the tablespace (`present` or `absent`).     | No       | `str`  | `present`, `absent` | `present` |
| `service_name` | The Oracle service name (SID or Service) to connect to.     | No       | `str`  | N/A               | N/A     |
| `sid`        | The Oracle SID to connect to (used if `service_name` is not provided). | No       | `str`  | N/A               | N/A     |
| `port`       | The port of the Oracle database.                             | No       | `int`  | N/A               | `1521`  |

## Author

- Gebz (@gebz97)

## Examples

### Create a New Tablespace

```yaml
- name: Create a tablespace
  gebz97.oradb.tablespace:
    tablespace: my_tablespace
    datafile: /u01/app/oracle/oradata/mydb/my_tablespace.dbf
    size: 100M
    autoextend: true
    maxsize: 1G
    service_name: ORCL
```

### Delete a Tablespace

```yaml
- name: Delete a tablespace
  gebz97.oradb.tablespace:
    tablespace: my_tablespace
    state: absent
    service_name: ORCL
```

## Return Values

| Key       | Description                                    | Type   | Returned |
|-----------|------------------------------------------------|--------|----------|
| `changed` | Whether the module made any changes.           | `bool` | always   |
| `msg`     | Informative message regarding the outcome.     | `str`  | always   |