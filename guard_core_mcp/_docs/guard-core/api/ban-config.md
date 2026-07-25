---

title: Ban Configuration
description: API reference for ThreatBanConfig and the per-category ban policy on SecurityConfig
keywords: threat ban config, per-category ban, auto ban, guard-core
---

Ban Configuration
=================

`ThreatBanConfig` is the per-category ban policy model. Combined with `SecurityConfig.threat_ban_config: dict[str, ThreatBanConfig]`, it lets each detection category carry its own threshold and ban duration. Categories not present in the dict fall through to the flat `auto_ban_threshold` / `auto_ban_duration` policy.

___

ThreatBanConfig
---------------

```python
class ThreatBanConfig(BaseModel):
    threshold: int = Field(ge=1)
    duration: int = Field(ge=1)
```

| Field       | Type | Description                                                  |
|-------------|------|--------------------------------------------------------------|
| `threshold` | `int` | Number of detections in this category before auto-ban (>= 1). |
| `duration`  | `int` | Ban duration in seconds (>= 1).                              |

___

SecurityConfig.threat_ban_config
--------------------------------

```python
class SecurityConfig(BaseModel):
    threat_ban_config: dict[str, ThreatBanConfig] = Field(default_factory=dict)
```

Keys must be valid category names from `ALL_DETECTION_CATEGORIES`. The validator rejects unknown keys with a `ValidationError`.

___

How the policy is applied
-------------------------

Every regex hit increments `suspicious_request_counts[ip][category]`. After a hit, the suspicious-activity check evaluates the bans in this order:

1. **Per-category ban** — for each category in the current detection result, look it up in `threat_ban_config`. If the IP's count for that category has reached or exceeded the entry's `threshold`, ban the IP with `entry.duration` seconds. The audit log carries `reason="penetration_attempt:<category>"`.
2. **Flat-threshold fallback** — if no per-category ban fired, sum all category counts for this IP. If the total has reached `auto_ban_threshold`, ban the IP for `auto_ban_duration` seconds. The audit log carries `reason="penetration_attempt"`.

If neither threshold is met, the request is rejected (status 400) but the IP is not banned.

___

Example
-------

Single-strike ban for SQL injection (week-long), 3-strike ban for XSS (one day), and the default flat policy for everything else:

```python
from guard_core.models import SecurityConfig, ThreatBanConfig

config = SecurityConfig(
    auto_ban_threshold=10,
    auto_ban_duration=3600,
    threat_ban_config={
        "sqli": ThreatBanConfig(threshold=1, duration=604800),
        "xss": ThreatBanConfig(threshold=3, duration=86400),
    },
)
```

A SQL injection hit on the first request bans the IP for one week with `reason="penetration_attempt:sqli"`. An XSS attempt on the third request bans for one day with `reason="penetration_attempt:xss"`. Twenty mixed `cmd_injection` and `recon` hits eventually trip the flat threshold and produce `reason="penetration_attempt"`.

___

See also
--------

- [SecurityConfig - Per-Category Bans](../configuration/security-config.md#per-category-bans)
- [Models - ThreatBanConfig](models.md#threatbanconfig)
- [DetectionResult](detection-result.md)
