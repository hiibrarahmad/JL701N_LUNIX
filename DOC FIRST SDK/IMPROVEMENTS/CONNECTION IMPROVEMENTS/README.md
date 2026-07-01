---
tags: [connection, bluetooth, tws, ble, ota, power, improvements, index, jl7016g]
date: 2026-06-08
status: IN PROGRESS — ACTIVE PLANNING
---

# 📡 Connection Improvements — Index

> 7 Bluetooth/TWS/BLE connection improvement opportunities identified from the JL7016G Hybrid SDK audit.
> [→ Back to IMPROVEMENTS/README.md](../README.md) | [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md)

---

## All Connection Improvements

| ID | Title | Effort | Risk | Status |
|---|---|---|---|---|
| [CONN-IMP-001](./CONN-IMP-001%20—%20Simultaneous%20TWS%20OTA%20Double-Bank%20Flash.md) | Simultaneous TWS OTA (Double-Bank Flash) | 🔴 High | 🔴 Needs 2 MB flash | ⏳ Pending |
| [CONN-IMP-002](./CONN-IMP-002%20—%20SPP%20Profile%20Enable.md) | SPP Profile Enable | 🟢 Low | ✅ Safe | ⏳ Pending |
| [CONN-IMP-003](./CONN-IMP-003%20—%20PBAP%20Phone%20Book%20Access%20Profile.md) | PBAP Phone Book Access Profile | 🟢 Low | ✅ Safe | ⏳ Pending |
| [CONN-IMP-004](./CONN-IMP-004%20—%20Low%20Power%20Mode%20Enable.md) | Low Power Mode Enable | 🟡 Medium | ⚠️ Test reconnect latency | ⏳ Pending |
| [CONN-IMP-005](./CONN-IMP-005%20—%20Auto-Shutdown%20Timer%20Tuning.md) | Auto-Shutdown Timer Tuning | 🟢 Low | ✅ Safe | ⏳ Pending |
| [CONN-IMP-006](./CONN-IMP-006%20—%20TWS%20Sibling%20Reconnect%20Optimization.md) | TWS Sibling Reconnect Optimization | 🟡 Medium | ⚠️ TWS stability | ⏳ Pending |
| [CONN-IMP-007](./CONN-IMP-007%20—%20BT%20Clock%20Frequency%20Power%20vs%20Performance.md) | BT Clock Frequency Optimization | 🟡 Medium | ⚠️ Per-mode testing | ⏳ Pending |

---

## Quick Context — Current Connection State

```
BT Spec:  BR 5.1 + EDR + BLE 5.x
Profiles: A2DP, HFP, HID, AVCTP, PNP  (SPP=OFF, PBAP=OFF)
TWS:      Auto-pair, PC5 L/R select, 4s sibling timeout
OTA:      Single-bank only (1 MB flash, no simultaneous TWS OTA)
Low Power: DISABLED (TCFG_LOWPOWER_LOWPOWER_SEL=0)
Auto-off:  180 s when idle/disconnected
BT Clocks: idle 24 MHz → connected 48 MHz → A2DP 96 MHz → call 64–96 MHz
```

---

## Related
- [→ TWS DEEP DIVE](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/TWS%20DEEP%20DIVE.md)
- [→ POWER DEEP DIVE](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/POWER%20DEEP%20DIVE.md)
- [→ POWER PRIORITY 01 (LDO vs Buck)](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/POWER%20PRIORITY%2001.md)
- [→ ARCHITECTURE/03-POWER-SYSTEM.md](../../SDK%20UPDATE%20FIXING/ARCHITECTURE/03-POWER-SYSTEM.md)
- [→ MAC ADDRESS PROVISIONING](../../SDK%20UPDATE%20FIXING/UPDATE/MAC%20ADDRESS%20PROVISIONING/)
