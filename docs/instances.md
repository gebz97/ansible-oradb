# Ansible Module: `gebz97.oradb.instances`

## Description

This module lists all currently running Oracle databases on a server by searching for Oracle instance processes.

## Version Added

- `1.0.0`

## Options

This module does not require any options.

## Examples

### List Running Oracle Databases

```yaml
- name: Get list of running Oracle databases
  gebz97.oradb.instances:
```

## Return Values

| Key        | Description                                          | Type   | Returned   | Sample                    |
|------------|------------------------------------------------------|--------|------------|----------------------------|
| `databases`| A list of currently running Oracle databases.        | `list` | always     | `['DB1', 'DB2', 'DB3']`    |
| `msg`      | Message indicating the result of the module execution.| `str`  | on failure | `No running Oracle databases found` |


## Author

- Gebz (@gebz97)