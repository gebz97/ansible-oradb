# Ansible Module: `gebz97.oradb.startup`

## Description

This module starts an Oracle database instance with optional startup modes such as restricted mode, and the ability to specify the Oracle SID.

## Version Added

- `1.0.0`

## Options

| Parameter    | Description                                                  | Required | Type   | Choices                        | Default |
|--------------|--------------------------------------------------------------|----------|--------|--------------------------------|---------|
| `sid`        | The Oracle SID of the database to start.                    | No       | `str`  | N/A                            | N/A     |
| `pfile`      | The path to the pfile/spfile if required for startup.        | No       | `str`  | N/A                            | N/A     |
| `mode`       | The startup mode for the Oracle database (`normal`, `mount`, `restrict`, or `force`). | No       | `str`  | `normal`, `mount`, `restrict`, `force` | `normal` |
| `oracle_home`| The ORACLE_HOME environment variable.                        | No       | `str`  | N/A                            | N/A     |
| `oracle_base`| The ORACLE_BASE environment variable.                        | No       | `str`  | N/A                            | N/A     |

## Author

- Gebz (@gebz97)

## Examples

### Start an Oracle Database in Normal Mode

```yaml
- name: Start Oracle database in normal mode
  gebz97.oradb.startup:
    sid: ORCL
```

### Start an Oracle Database in Restricted Mode

```yaml
- name: Start Oracle database in restricted mode
  gebz97.oradb.startup:
    sid: ORCL
    mode: restrict
```

### Start an Oracle Database with a Specific Pfile

```yaml
- name: Start Oracle database with pfile
  gebz97.oradb.startup:
    sid: ORCL
    pfile: /u01/app/oracle/dbs/initORCL.ora
```

## Return Values

| Key       | Description                                    | Type   | Returned |
|-----------|------------------------------------------------|--------|----------|
| `changed` | Whether the database was started or not.       | `bool` | always   |
| `msg`     | Informative message regarding the outcome.     | `str`  | always   |