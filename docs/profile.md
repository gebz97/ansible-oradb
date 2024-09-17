# Ansible Module: `gebz97.oradb.profile`

## Description

This module allows you to create, modify, and delete Oracle database profiles.

## Version Added

- `1.0.0`

## Options

| Parameter      | Description                                                         | Required | Type   | Choices            | Default   |
|----------------|---------------------------------------------------------------------|----------|--------|--------------------|-----------|
| `profile`      | Name of the profile to manage.                                      | Yes      | `str`  | N/A                | N/A       |
| `limits`       | Dictionary of resource limits for the profile.                      | No       | `dict` | N/A                | N/A       |
| `state`        | Desired state of the profile (`present` or `absent`).               | No       | `str`  | `present`, `absent` | `present` |
| `service_name` | The Oracle service name (SID or Service) to connect to.              | No       | `str`  | N/A                | N/A       |
| `sid`          | The Oracle SID to connect to (used if `service_name` is not provided).| No       | `str`  | N/A                | N/A       |
| `port`         | The port of the Oracle database.                                    | No       | `int`  | N/A                | `1521`    |

## Author

- Gebz (@gebz97)

## Examples

### Create a New Profile with Limits

```yaml
- name: Create a profile with limits
  gebz97.oradb.profile:
    profile: my_profile
    limits:
      SESSIONS_PER_USER: 10
      CPU_PER_SESSION: 10000
    service_name: ORCL
```

### Modify a Profile by Adding Limits

```yaml
- name: Modify profile by adding limits
  gebz97.oradb.profile:
    profile: my_profile
    limits:
      CPU_PER_CALL: 1000
    service_name: ORCL
```

### Delete a Profile

```yaml
- name: Delete a profile
  gebz97.oradb.profile:
    profile: my_profile
    state: absent
    service_name: ORCL
```

## Return Values

| Key       | Description                                | Type    | Returned |
|-----------|--------------------------------------------|---------|----------|
| `changed` | Whether the module made any changes.       | `bool`  | always   |
| `msg`     | Informative message regarding the outcome. | `str`   | always   |