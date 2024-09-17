# Ansible Module: `gebz97.oradb.param`

## Description

This module allows you to create, modify, delete, and convert Oracle PFILE and SPFILE configurations with validated parameters.

## Version Added

- `1.0.0`

## Options

| Parameter   | Description                                                          | Required | Type   | Choices                    | Default   |
|-------------|----------------------------------------------------------------------|----------|--------|----------------------------|-----------|
| `pfile`     | Path to the PFILE to manage.                                          | No       | `str`  | N/A                        | N/A       |
| `spfile`    | Path to the SPFILE to manage.                                         | No       | `str`  | N/A                        | N/A       |
| `sid`       | The Oracle system identifier (SID).                                   | No       | `str`  | N/A                        | N/A       |
| `state`     | Desired state of the file (`present` or `absent`).                    | No       | `str`  | `present`, `absent`         | `present` |
| `action`    | Action to perform on the file (`create`, `modify`, `delete`, `convert`).| Yes      | `str`  | `create`, `modify`, `delete`, `convert` | N/A |
| `parameters`| Dictionary of PFILE/SPFILE parameters to manage.                      | No       | `dict` | N/A                        | N/A       |

## Author

- Gebz (@gebz97)

## Examples

### Create a New PFILE

```yaml
- name: Create a PFILE with parameters
  gebz97.oradb.param:
    pfile: /u01/app/oracle/dbs/init.ora
    sid: ORCL
    action: create
    parameters:
      db_cache_size: 104857600
      sga_target: 209715200
```

### Modify an SPFILE

```yaml
- name: Modify SPFILE with new parameters
  gebz97.oradb.param:
    spfile: /u01/app/oracle/dbs/spfileORCL.ora
    action: modify
    parameters:
      processes: 300
```

### Delete a PFILE

```yaml
- name: Delete an old PFILE
  gebz97.oradb.param:
    pfile: /u01/app/oracle/dbs/init.ora
    action: delete
```

### Convert PFILE to SPFILE

```yaml
- name: Convert PFILE to SPFILE
  gebz97.oradb.param:
    pfile: /u01/app/oracle/dbs/init.ora
    spfile: /u01/app/oracle/dbs/spfileORCL.ora
    action: convert
```

## Return Values

| Key               | Description                                                | Type   | Returned   | Sample                                    |
|-------------------|------------------------------------------------------------|--------|------------|--------------------------------------------|
| `original_message`| The original parameters that were passed.                  | `dict` | always     | `{"db_cache_size": 104857600, "sga_target": 209715200}` |
| `message`         | The output message indicating the result of the action.    | `str`  | always     | `"PFILE created successfully"`            |
| `changed`         | Indicates if the module made any changes.                  | `bool` | always     | `true`                                     |