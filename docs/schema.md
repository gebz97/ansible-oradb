# Ansible Module: `gebz97.oradb.schema`

## Description

This module allows you to manage Oracle database schemas, including creating, modifying, and deleting schemas, with optional support for assigning tablespaces.

## Version Added

- `1.0.0`

## Options

| Parameter        | Description                                                        | Required | Type     | Choices                | Default   |
|------------------|--------------------------------------------------------------------|----------|----------|------------------------|-----------|
| `schema`         | Name of the schema to manage.                                      | Yes      | `str`    | N/A                    | N/A       |
| `password`       | Password for the schema.                                           | No       | `str`    | N/A                    | N/A       |
| `tablespace`     | Default tablespace for the schema.                                 | No       | `str`    | N/A                    | N/A       |
| `temp_tablespace`| Temporary tablespace for the schema.                               | No       | `str`    | N/A                    | N/A       |
| `state`          | Desired state of the schema (`present` or `absent`).               | No       | `str`    | `present`, `absent`     | `present` |
| `service_name`   | The Oracle service name (SID or Service) to connect to.            | No       | `str`    | N/A                    | N/A       |
| `sid`            | The Oracle SID to connect to (used if `service_name` is not set).  | No       | `str`    | N/A                    | N/A       |
| `port`           | The port of the Oracle database.                                   | No       | `int`    | N/A                    | `1521`    |

## Author

- Gebz (@gebz97)

## Examples

### Create a New Schema with Default Tablespace

```yaml
- name: Create a schema with default tablespace
  gebz97.oradb.schema:
    schema: my_schema
    password: MyStrongPassword!
    tablespace: users
    temp_tablespace: temp
    service_name: ORCL
```

### Delete a Schema

```yaml
- name: Delete a schema
  gebz97.oradb.schema:
    schema: my_schema
    state: absent
    service_name: ORCL
```

## Return Values

| Key       | Description                                | Type    | Returned |
|-----------|--------------------------------------------|---------|----------|
| `changed` | Whether the module made any changes.       | `bool`  | always   |
| `msg`     | Informative message regarding the outcome. | `str`   | always   |