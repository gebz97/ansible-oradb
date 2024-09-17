# Ansible Module: `gebz97.oradb.shutdown`

## Description

This module shuts down an Oracle database instance with various options such as immediate, normal, transactional, or abort shutdown.

## Version Added

- `1.0.0`

## Options

| Parameter | Description                                           | Required | Type   | Choices                                    | Default   |
|-----------|-------------------------------------------------------|----------|--------|--------------------------------------------|-----------|
| `sid`     | The Oracle SID of the instance to shut down.         | Yes      | `str`  | N/A                                        | N/A       |
| `mode`    | The shutdown mode (`IMMEDIATE`, `NORMAL`, `TRANSACTIONAL`, or `ABORT`). | No       | `str`  | `IMMEDIATE`, `NORMAL`, `TRANSACTIONAL`, `ABORT` | `IMMEDIATE` |
| `force`   | Whether to force the shutdown if there are any issues. | No       | `bool` | N/A                                        | `false`   |

## Author

- Gebz (@gebz97)

## Examples

### Shutdown an Oracle Instance with Immediate Mode

```yaml
- name: Shutdown Oracle instance immediately
  gebz97.oradb.shutdown:
    sid: ORCL
    mode: IMMEDIATE
```

### Shutdown an Oracle Instance Normally

```yaml
- name: Normal shutdown of Oracle instance
  gebz97.oradb.shutdown:
    sid: ORCL
    mode: NORMAL
```

### Forcefully Shutdown an Oracle Instance with Abort Mode

```yaml
- name: Forcefully shutdown Oracle instance
  gebz97.oradb.shutdown:
    sid: ORCL
    mode: ABORT
    force: true
```