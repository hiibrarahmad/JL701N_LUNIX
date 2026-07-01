---
tags: [fix, tws, key-table, architecture, compile-time, master-slave, key-event, design-finding]
date: 2026-05-04
status: COMPLETE & DEPLOYED
severity: INVESTIGATION — Compile-time per-bud key table splits are ineffective in TWS; removed and documented
files_changed: [apps/earphone/board/br28/board_jl7016g_hybrid.c, apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h]
related: [FIX-022]
---

# FIX-021 — Per-Bud Key Table Split Doesn't Work in TWS

**Status:** COMPLETE & DEPLOYED  
**Build:** SUCCESS (0 errors, ota.bin generated)  
**Date:** May 4, 2026  
**Chip:** AC701N (BR28 core)  
**Board:** JL7016G Hybrid  

---

## Symptom

After adding a `#if TCFG_RIGHT_BUD` split in the KEY_2 row of `key_table[]`, both buds continued to perform the same action (VOL_DOWN / Prev) regardless of which physical bud was touched. Setting `TCFG_RIGHT_BUD 1` in cfg.h and flashing had no effect on the right bud's behaviour. Both buds behaved identically as if only the LEFT bud mapping was active.

---

## Root Cause — TWS Master Owns All Key Event Dispatch

In a TWS pair, **only the master processes app-level key events**. This is a fundamental architectural property of the JL TWS SDK, not a bug. Here is the exact sequence from a slave touch to an executed action:

```
[SLAVE BUD — left bud, PB4 touched]
  LP touch driver detects touch (lp_touch_key.c)
  └─ driver fires key event locally
  └─ TWS layer intercepts before app_earphone_key_event_handler() is called
  └─ packages event as TWS message with arg = KEY_EVENT_FROM_TWS
  └─ sends raw event over TWS BT link to master

[MASTER BUD — right bud, receives forwarded event]
  Receives TWS message
  └─ calls app_earphone_key_event_handler(event)
        where event->arg == KEY_EVENT_FROM_TWS
  └─ looks up MASTER'S key_table[key->value][key->event]
  └─ executes action from MASTER'S table
  [SLAVE'S key_table is NEVER consulted]
```

This means: no matter what the slave bud's key_table says, it is **completely irrelevant** at runtime. The master's table handles everything.

### Why `#if TCFG_RIGHT_BUD` Makes It Worse

When the right bud is master and has `TCFG_RIGHT_BUD 1`, its KEY_2 HOLD is set to `KEY_VOL_UP`. Good so far. But the left bud (slave) has `TCFG_RIGHT_BUD 0` and its KEY_2 HOLD is `KEY_VOL_DOWN` — this value only ever exists in the slave's compiled binary and is **never read** by the master when the slave's touch is forwarded.

The master has `TCFG_RIGHT_BUD 1`, so when the **slave's touch arrives at the master** as a forwarded event, the master looks up its own table — which says `KEY_VOL_UP` for all KEY_2 holds. Both buds act as right bud.

Even worse: **master/slave role can flip** between connection cycles. If the left bud happens to become master, the right bud's touches will be dispatched through the LEFT bud's table (compiled with `TCFG_RIGHT_BUD 0`) — so the right bud suddenly performs left-bud actions.

### The Fundamental Rule

> **In a TWS system, the master evaluates its own `key_table[]` for ALL events, including events forwarded from the slave.** Compile-time per-bud key table splits are meaningless for any key that behaves differently per bud.

---

## Why People Think It Should Work

The intuition is: "build the right bud firmware with `TCFG_RIGHT_BUD=1`, build the left bud firmware with `TCFG_RIGHT_BUD=0`, flash each device differently, and they do different things on hold." This logic would hold **only in a single-bud standalone context** where each bud runs its own app handler independently. As soon as TWS connects and a master is elected, the master's table is authoritative for both physical buds.

---

## Resolution

The `#if TCFG_RIGHT_BUD` key table split was removed from the KEY_2 row. The correct solution is runtime channel detection in the key event handler using `key_tws_lr_diff_deal()` — see **FIX-022**. This approach works regardless of which bud is currently master.

---

## Files Changed

| File | Change |
|------|--------|
| `apps/earphone/board/br28/board_jl7016g_hybrid.c` | Removed `#if TCFG_RIGHT_BUD` split from KEY_2 row; restored single neutral row (`KEY_VOL_UP` + `KEY_MUSIC_NEXT`) |
| `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h` | `TCFG_RIGHT_BUD` flag retained but no longer used for key table split |

---

## Related Documents

- [FIX-022 — Channel-Aware Dispatch](./FIX-022%20—%20Right%20Bud%20Vol%20Up%20Left%20Bud%20Vol%20Down%20Channel-Aware%20Dispatch.md) — the correct runtime solution
- [FIX-020 — TWS Volume Desync](./FIX-020%20—%20TWS%20Volume%20Desync%20Between%20Buds.md) — companion volume sync fix
