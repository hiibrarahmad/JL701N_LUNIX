---
tags: [connection, power, auto-shutdown, timer, battery, ux, jl7016g, improvement]
date: 2026-06-08
status: PLANNED — UX PREFERENCE DECISION NEEDED
effort: 🟢 Low
risk: ✅ Safe — single constant change, no hardware or protocol effect
priority: ⭐ 5 — Low effort, direct UX + battery impact
---

# 📡 CONN-IMP-005 — Auto-Shutdown Timer Tuning

> **One-line summary:** The earphone auto-powers off after 180 seconds (3 minutes) of disconnection. This value should be tuned based on product UX requirements — too short frustrates users who briefly lose connection; too long wastes battery when earphones are left out of case.

---

## Current State

Auto-shutdown after 3 minutes of idle disconnection:

```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_AUTO_SHUT_DOWN_TIME    180   // seconds — 3 minutes
```

The timer starts when:
- No Bluetooth device is connected
- The earbud is not in the charger case

The timer resets when:
- A BT device connects
- The earbud is inserted into the charging case

---

## The UX Problem with 180 Seconds

### Too Short for These Scenarios

| Scenario | Time Before Shutdown | User Experience |
|---|---|---|
| Phone drops Bluetooth briefly (stair, door) | < 30 s reconnect, timer already running | Earphone may shut down during short disconnect |
| User pauses music and walks away | 3 min = forces shutdown | Must power on again when they return |
| Removing earphones temporarily (30 min break) | Shutdown after 3 min | Must re-pair or press power button |
| TWS sibling loses connection briefly | Timer starts immediately | One bud shuts down, other stays on |

### Too Long for These Scenarios

| Scenario | Time Before Shutdown | User Experience |
|---|---|---|
| Left out of case overnight | Never shuts down for 3 min | Drains battery completely |
| Forgotten in bag (not in case) | 3 min then off — acceptable | Fine |

---

## Recommended Tuning Options

| Scenario | Recommended Value | Rationale |
|---|---|---|
| Consumer product (AirPods-like) | **300 seconds (5 min)** | Comfortable for brief disconnects |
| Developer / frequent reconnect | **600 seconds (10 min)** | Less frustration during testing |
| Maximum battery conservation | **60 seconds (1 min)** | Aggressive — always use case |
| Production default (recommended) | **300 seconds** | Balances UX and battery |

### Recommended Change

```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_AUTO_SHUT_DOWN_TIME    300   // 5 minutes (was 180 = 3 minutes)
```

---

## Secondary Timer — TWS Sibling Pairing Timeout

Related setting that also affects behavior after disconnection:

```c
#define CONFIG_TWS_CONNECT_SIBLING_TIMEOUT    4   // seconds
```

This is the window in which the earphone waits for its TWS sibling to appear after boot. If the sibling does not appear within 4 seconds, the bud enters solo mode. See [→ CONN-IMP-006](./CONN-IMP-006%20—%20TWS%20Sibling%20Reconnect%20Optimization.md) for full analysis.

---

## Additional State: Power-on Without Key Press

```c
#define TCFG_POWER_ON_NEED_KEY    0   // earphone powers on without key press
```

If `POWER_ON_NEED_KEY=0`, removing from case powers on immediately. Combined with a short auto-shutdown, this means frequent case opens/closes consume more cycles. With a longer timer it is less of an issue.

---

## Risk & Trade-offs

| Aspect | Assessment |
|---|---|
| Battery waste if timer too long | Minor — earphone at connected-idle uses ~15–20 mA; +2 min = ~0.5 mAh |
| User frustration if too short | Significant — must manually power on; reconnect takes 2–5 s |
| Change complexity | 1 constant in 1 file — trivial |
| Reversible | Yes — change constant and rebuild |

---

## Verification Steps

1. Change constant to 300 and rebuild
2. Pair earphone with phone
3. Turn off Bluetooth on phone (simulate disconnect)
4. Start timer: earphone should remain on for 5 minutes
5. At 5 minutes: confirm earphone powers off (UART shows `auto_shutdown` message)
6. Re-enable phone BT within the 5-minute window: confirm earphone reconnects before shutdown

---

## Related
- [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md) — Section 5
- [→ CONN-IMP-004 Low Power Mode](./CONN-IMP-004%20—%20Low%20Power%20Mode%20Enable.md) — Low power during idle is separate from shutdown
- [→ CONN-IMP-006 TWS Sibling Reconnect](./CONN-IMP-006%20—%20TWS%20Sibling%20Reconnect%20Optimization.md)
- [→ POWER DEEP DIVE](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/POWER%20DEEP%20DIVE.md)
