---
tags: [fix, key-event, ch1, pb1, gpio, pc3, suppress, ctmu]
date: 2026-05-04
status: COMPLETE & DEPLOYED
severity: BUG — PB1 touch was triggering music play/pause, next track, etc.
files_changed: [cpu/br28/lp_touch_key.c]
---

# FIX-018: PB1 (CH1) Generates App Key Events — Suppress; GPIO-Only Role

**Status:** COMPLETE & DEPLOYED  
**Build:** SUCCESS (0 errors, ota.bin generated)  
**Date:** May 4, 2026  

---

## Problem

After FIX-016 and FIX-017, PB1 was fully operational. However, touching PB1 was also firing music control actions (play/pause, next track, volume up/down) in addition to driving PC3 high/low.

### Boot log evidence

```
[00:06:04.568][Debug]: [LP_KEY]CH1: FALLING
[00:06:04.728][Debug]: [LP_KEY]CH1: RAISING
[00:06:05.131][Debug]: [LP_KEY]notify key1 short event, cnt: 1
[00:06:05.137][LP_KEY]CH1_DETECTED: type=1
[00:06:05.146][Info]:  [KEY_EVENT_DEAL]key_event:12 2 0   ← KEY_MUSIC_PP dispatched
```

`key_event:12 2 0` → event type 12 = `KEY_EVENT_CLICK`, value 2 → `key_table[2][CLICK]` = `KEY_MUSIC_PP` (play/pause). Every SHORT, LONG, and HOLD on PB1 was reaching the system event queue and triggering real audio actions.

### Expected behaviour

- **PB1 (CH1 / eartch primary):** Touch-only GPIO feedback pin. Its job is to drive PC3 **LOW** on FALLING (touch down) and **HIGH** on RAISING (touch release). Idle state is HIGH. **It must not generate any key events.**
- **PB4 (CH3 / eartch ref):** All music/volume/call control. SHORT = play/pause, DOUBLE = next track, TRIPLE = voice assistant, LONG = vol up, HOLD = vol up.

---

## Root Cause

`__ctmu_notify_key_event()` in `cpu/br28/lp_touch_key.c` is the single path through which ALL channel key events (SHORT, LONG, HOLD, UP) reach `sys_event_notify()`.

There was no guard to prevent CH1 from dispatching into the system event queue. Even though CH1 is the `eartch_ch` (primary in-ear channel), the only existing guard was:

```c
#if !TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE
    if (__this->config->eartch_en && (ch == __this->config->eartch_ch)) {
        return;  // ← only active when macro is 0
    }
#endif
```

`TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE` is defined as `1` (required for CH1 FALLING/RAISING processing in earlier fixes), so this guard was **compiled out**. CH1 key events fell through to `sys_event_notify()` unconditionally.

The FALLING and RAISING raw hardware events that drive PC3 are handled in a separate code path (the M2P CTMU event handler) before `__ctmu_notify_key_event()` is called — so suppressing here does not affect PC3 GPIO behaviour.

---

## Fix

**File:** `cpu/br28/lp_touch_key.c`  
**Function:** `__ctmu_notify_key_event()`

Added a return guard just before `sys_event_notify()`, reusing the existing `TCFG_LP_TOUCH_PB1_LED_FEEDBACK_ENABLE` config macro:

```c
#if TCFG_LP_TOUCH_PB1_LED_FEEDBACK_ENABLE
    /* PB1 (CH1 = eartch primary) is a GPIO-only feedback pin.
     * FALLING/RAISING still fire and drive PC3 high/low, but
     * SHORT / LONG / HOLD key events must not reach the system —
     * those are handled exclusively by PB4 (CH3 = eartch ref). */
    if (__this->config->eartch_en && (ch == __this->config->eartch_ch)) {
        return;
    }
#endif
```

This guard activates only when `TCFG_LP_TOUCH_PB1_LED_FEEDBACK_ENABLE = 1` (set in `board_jl7016g_hybrid_cfg.h`). It intercepts CH1 after all event bookkeeping (`last_key`, `click_cnt`, timers) has already been settled, but before `sys_event_notify()` sends the event to the application layer.

---

## Before / After

| Scenario | Before FIX-018 | After FIX-018 |
|----------|---------------|---------------|
| PB1 short tap | PC3 LOW→HIGH + `KEY_MUSIC_PP` fires | PC3 LOW→HIGH only — no app event |
| PB1 long press | PC3 LOW→HIGH + `KEY_VOL_UP` fires | PC3 LOW→HIGH only — no app event |
| PB1 hold | PC3 LOW→HIGH + `KEY_VOL_UP` repeats | PC3 LOW→HIGH only — no app event |
| PB4 short tap | `KEY_MUSIC_PP` (unchanged) | `KEY_MUSIC_PP` (unchanged) |
| PB4 double tap | `KEY_MUSIC_NEXT` (unchanged) | `KEY_MUSIC_NEXT` (unchanged) |
| PB4 long press | `KEY_VOL_UP` (unchanged) | `KEY_VOL_UP` (unchanged) |

---

## Key Event Flow (After All Fixes)

```
PB1 TOUCH DOWN
  └─ CTMU FALLING event
       ├─ gpio_write(PC3, LOW)           ← PC3 output, ACTIVE (LOW)
       └─ __ctmu_notify_key_event()
            └─ [FIX-018 guard] return    ← SUPPRESSED, never reaches sys_event_notify

PB1 TOUCH RELEASE
  └─ CTMU RAISING event
       ├─ gpio_write(PC3, HIGH)          ← PC3 output, IDLE (HIGH)
       └─ __ctmu_notify_key_event()
            └─ [FIX-018 guard] return    ← SUPPRESSED

PB4 TOUCH DOWN/RELEASE
  └─ CTMU FALLING / RAISING event
       └─ __ctmu_notify_key_event()
            └─ [FIX-018 guard] ch != eartch_ch → passes
                 └─ sys_event_notify()   ← KEY_MUSIC_PP, KEY_VOL_UP, etc.
```

---

## Config Dependencies

| Macro | Value | Effect |
|-------|-------|--------|
| `TCFG_LP_TOUCH_PB1_LED_FEEDBACK_ENABLE` | `1` | Activates FIX-018 guard + PC3 GPIO init + FALLING/RAISING GPIO calls |
| `TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE` | `1` | Keeps FALLING/RAISING processing active for CH1 (do not change) |
| `lp_touch_key_config.eartch_ch` | `1` (CH1) | Identifies which channel is suppressed |

---

## Verification

After flashing the new `ota.bin`:

**Expected serial output — PB1 tap:**
```
[LP_KEY]CH1: FALLING
[LP_KEY]CH1: RAISING
[LP_KEY]notify key1 short event, cnt: 1
[LP_KEY]CH1_DETECTED: type=1
```
No `[KEY_EVENT_DEAL]key_event` line should follow — the event is swallowed before it reaches that layer.

**Expected serial output — PB4 tap:**
```
[LP_KEY]CH3: FALLING
[LP_KEY]CH3: RAISING
[LP_KEY]notify key3 short event, cnt: 1
[KEY_EVENT_DEAL]key_event:12 2 0   ← KEY_MUSIC_PP, value=2
```
