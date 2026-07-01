---
tags: [fix, key-event, poweroff, key_value, pb1, hold, ch1]
date: 2026-05-01
status: COMPLETE & DEPLOYED
severity: BUG — Holding PB1 triggered soft power-off
files_changed: [apps/earphone/board/br28/board_jl7016g_hybrid.c]
---

# FIX-017: PB1 Hold Triggers Power-Off (key_value Fix)

**Status:** COMPLETE & DEPLOYED
**Build:** SUCCESS (0 errors, ota.bin generated)
**Date:** May 1, 2026

---

## Problem

After FIX-015 and FIX-016 made PB1 fully functional, a new symptom appeared: **holding PB1 for ~2 seconds powered off the device.** Holding PB4 for the same duration did nothing — it just repeated volume-up.

### Boot log evidence

Holding PB1:
```
[LP_KEY]CH1: HOLD click
[KEY_EVENT_DEAL]key_event:11 0 2       ← event=HOLD, key_value=0
[KEY_EVENT_DEAL]poweroff flag:1 cnt:0
[KEY_EVENT_DEAL]poweroff flag:1 cnt:1
...
[KEY_EVENT_DEAL]poweroff flag:1 cnt:5
[EARPHONE]sys_enter_soft_poweroff, 0   ← device powers off
```

Holding PB4:
```
[LP_KEY]CH3: HOLD click
[KEY_EVENT_DEAL]key_event:15 2 2       ← event=HOLD, key_value=2
```
No poweroff. No counter.

---

## Root Cause

The key event dispatcher in `key_event_deal.c` looks up actions in a 2D table:

```c
key_event = key_table[key->value][key->event];
```

The `key_table` in `board_jl7016g_hybrid.c`:

```c
//                  SHORT           LONG              HOLD
// KEY_0 (value=0): KEY_MUSIC_PP,   KEY_POWEROFF,     KEY_POWEROFF_HOLD,  ...
// KEY_1 (value=1): KEY_MUSIC_NEXT, KEY_VOL_UP,       KEY_VOL_UP,         ...
// KEY_2 (value=2): KEY_MUSIC_PP,   KEY_VOL_UP,       KEY_VOL_UP,         ...
```

**CH1 (PB1) had `ch[1].key_value = 0`** → LONG and HOLD mapped to `KEY_POWEROFF` and `KEY_POWEROFF_HOLD`.
**CH3 (PB4) has `ch[3].key_value = 2`** → LONG and HOLD mapped to `KEY_VOL_UP`.

This is why holding PB1 powered off the device and holding PB4 did not.

---

## Fix

**File:** `apps/earphone/board/br28/board_jl7016g_hybrid.c`

```c
// Before:
.ch[1].key_value = 0,    // KEY_0 row → HOLD = KEY_POWEROFF_HOLD

// After:
.ch[1].key_value = 2,    // KEY_2 row → HOLD = KEY_VOL_UP
```

One line change. CH1 now uses the same action row as CH3. Their behaviour is now identical for every event type.

---

## Key Table Context

```c
// board_jl7016g_hybrid.c — full key_table
u8 key_table[KEY_NUM_MAX][KEY_EVENT_MAX] = {
    //         SHORT            LONG              HOLD              UP        DOUBLE           TRIPLE
    {KEY_MUSIC_PP,  KEY_POWEROFF,    KEY_POWEROFF_HOLD, KEY_NULL, KEY_CALL_LAST_NO, KEY_ANC_SWITCH},  // KEY_0
    {KEY_MUSIC_NEXT,KEY_VOL_UP,      KEY_VOL_UP,        KEY_NULL, KEY_OPEN_SIRI,    KEY_NULL},         // KEY_1
    {KEY_MUSIC_PP,  KEY_VOL_UP,      KEY_VOL_UP,        KEY_NULL, KEY_MUSIC_NEXT,   KEY_OPEN_SIRI},    // KEY_2 ← CH1+CH3
};
```

KEY_0 is reserved for a physical button (or a touch key that needs power-off on hold). CH1 and CH3 are both touch pads — the intended behaviour is volume control on hold, not power-off.

---

## Channel-to-key_value Mapping (after fix)

| Channel | GPIO | key_value | LONG action | HOLD action |
|---|---|---|---|---|
| CH0 | PB0 | 0 | KEY_POWEROFF | KEY_POWEROFF_HOLD |
| CH1 | **PB1** | **2** | KEY_VOL_UP | KEY_VOL_UP |
| CH2 | PB2 | 1 | KEY_VOL_UP | KEY_VOL_UP |
| CH3 | **PB4** | **2** | KEY_VOL_UP | KEY_VOL_UP |
| CH4 | PB5 | 3 | — | — |

---

## Verification

After flashing, hold PB1:
- Boot log shows `key_event:XX 2 2` (key_value=2, event=HOLD) — no poweroff counter
- Device stays on
- Volume increases (same as holding PB4)

---

## Related Documents

- [01-TOUCH-SYSTEM.md](../ARCHITECTURE/01-TOUCH-SYSTEM.md) — System overview with full key routing
- [FIX-016 — PC3 GPIO Touch Feedback](./FIX-016%20—%20PB1%20PC3%20GPIO%20Touch%20Feedback.md) — the preceding fix
- [FIX-015 — PB1 Complete Solution](./FIX-015%20—%20PB1_COMPLETE_SOLUTION.md) — earlier CH1 work
