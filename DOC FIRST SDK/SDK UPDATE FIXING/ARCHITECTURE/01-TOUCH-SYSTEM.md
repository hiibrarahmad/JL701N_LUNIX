---
tags: [architecture, touch, input, ctmu, gpio, pb1, pc3, key-event]
date: 2026-05-01
updated: 2026-05-04
---

# Touch Input System — Full Architecture

**Purpose:** Complete reference for how CTMU capacitive touch is processed, routed to key events, and drives GPIO outputs on the JL7016G (BR28) earphone SoC.

---

## 1. Document Architecture Map

This is the **master navigation index** for all touch-system documentation:

```
SDK UPDATE FIXING/
├── ARCHITECTURE/
│   └── 01-TOUCH-SYSTEM.md          ← you are here — full system overview
│
├── FIXING/
│   ├── FIX-015 — PB1_COMPLETE_SOLUTION.md          ← CH1 unblocking, threshold, sensitivity
│   ├── FIX-016 — PB1 PC3 GPIO Touch Feedback.md    ← PC3 output feature
│   ├── FIX-017 — PB1 Hold Power-Off Fix.md          ← key_value=2 prevents power-off
│   ├── FIX-018 — PB1 Key Events Suppressed GPIO Only.md  ← PB1 now GPIO-only, PB4 handles app events
│   └── FIX-019 — PC3 Polarity Inverted (Active LOW).md  ← PC3 LOW while touched (active-low)
│
└── SDKDOCUMENT/
    └── PB4_TOUCH_AND_INEAR_BEHAVIOR.md      ← reference: how CH3 works (model for CH1)
```

**How to navigate:**
- Start here for the big picture.
- Go to FIXING/FIX-0xx for the step-by-step record of any specific change.
- Go to SDKDOCUMENT for hardware-level reference material.

---

## 2. System Hardware Overview

### Active Touch Channels

| CTMU Channel | GPIO Pin | Role | key_value |
|---|---|---|---|
| **CH1** | PB1 | Primary touch key + in-ear sense | **2** (FIX-017) |
| **CH3** | PB4 | Reference in-ear sense + touch key | **2** |

### Register State (verified from boot log)

```
M2P_CTMU_CH_ENABLE      = 0x0a   → CH1 + CH3 enabled
M2P_CTMU_EARTCH_CH      = 0x31   → CH1 primary, CH3 reference
M2P_CTMU_CH_CFG         = 0x00   → EARTCH hardware mode OFF (FIX-016)
M2P_CTMU_CH_WAKEUP_EN   = 0x02   → CH1 wakeup enabled
```

### PC3 GPIO Output

| Signal | Direction | Function |
|---|---|---|
| PC3 (IO_PORTC_03) | Output | LOW while PB1 is actively touched (active-LOW — FIX-019) |

---

## 3. Full Event Flow — From Finger Touch to PC3 Output

```
Finger touches PB1
        │
        ▼
CTMU CH1 capacitance threshold crossed
        │  (hardware event, ~50 µs)
        ▼
CTMU_P2M_CH1_FALLING_EVENT fires
  in: lp_touch_key_event_handler()   [cpu/br28/lp_touch_key.c]
        │
        ├──► gpio_write(IO_PORTC_03, 0)   ← PC3 goes LOW immediately  (active-LOW, FIX-019)
        │      [guarded by TCFG_LP_TOUCH_PB1_LED_FEEDBACK_ENABLE]
        │
        ├──► TouchAlgo_Init() adaptive algorithm runs for CH1
        │
        └──► ctmu_fall_click_handle(ch_num)
                │
                ▼
         Timer tracks SHORT / LONG / HOLD durations
                │
                ├── SHORT  → key_event(ch_num, KEY_EVENT_CLICK)  [suppressed by FIX-018]
                ├── LONG   → key_event(ch_num, KEY_EVENT_LONG)   [suppressed by FIX-018]
                └── HOLD   → key_event(ch_num, KEY_EVENT_HOLD)   [suppressed by FIX-018]

Finger leaves PB1
        │
        ▼
CTMU_P2M_CH1_RAISING_EVENT fires
        │
        ├──► gpio_write(IO_PORTC_03, 1)   ← PC3 goes HIGH  (back to idle HIGH, FIX-019)
        │      [guarded by TCFG_LP_TOUCH_PB1_LED_FEEDBACK_ENABLE]
        │
        └──► ctmu_raise_click_handle(ch_num)
                │
                ▼
         key_event(ch_num, KEY_EVENT_UP)  [suppressed by FIX-018]
```

**Key point:** PC3 tracks the raw capacitive state — LOW for the entire duration the finger is on PB1, HIGH the moment it lifts off (and at idle). This is independent of SHORT/LONG/HOLD timers. All CH1 key events are suppressed by FIX-018; PC3 is the only output.

---

## 4. Key Event Routing

Events from CH1 carry `key_value = 2` and are dispatched to `key_event_deal.c`:

```c
// key_table[key_value][event_type]  in board_jl7016g_hybrid.c
//                  SHORT           LONG          HOLD          UP    DOUBLE        TRIPLE
// KEY_0 (value=0): KEY_MUSIC_PP,   KEY_POWEROFF, KEY_POWEROFF_HOLD, ...    // ← DANGER: power-off
// KEY_2 (value=2): KEY_MUSIC_PP,   KEY_VOL_UP,   KEY_VOL_UP,        ...    // ← safe, CH1+CH3
```

CH1 (PB1) uses `key_value = 2` — same row as CH3 (PB4). This means LONG and HOLD on PB1 adjust volume, not power off the device. See FIX-017.

---

## 5. PC3 GPIO Feedback — Exact Code Location

**File:** `cpu/br28/lp_touch_key.c`

**FALLING handler (touch down → PC3 LOW, active-LOW):**
```c
case CTMU_P2M_CH1_FALLING_EVENT:
    ...
#if TCFG_LP_TOUCH_PB1_LED_FEEDBACK_ENABLE
    // CH1 (PB1) touch active: drive PC3 LOW
    if (ch_num == 1) {
        gpio_write(TCFG_LP_TOUCH_PB1_LED_PORT, !TCFG_LP_TOUCH_PB1_LED_ACTIVE_LEVEL);
    }
#endif
    break;
```

**RAISING handler (touch up → PC3 HIGH, idle):**
```c
case CTMU_P2M_CH1_RAISING_EVENT:
    ...
#if TCFG_LP_TOUCH_PB1_LED_FEEDBACK_ENABLE
    // CH1 (PB1) touch released: drive PC3 HIGH
    if (ch_num == 1) {
        gpio_write(TCFG_LP_TOUCH_PB1_LED_PORT, TCFG_LP_TOUCH_PB1_LED_ACTIVE_LEVEL);
    }
#endif
```

**Note:** This is NOT in `lp_touch_key_event_remap()`. It fires at the raw hardware event level — before debounce timers, before key classification.

---

## 6. Configuration (board_jl7016g_hybrid_cfg.h)

```c
// PC3 GPIO output tied to PB1 touch state
#define TCFG_LP_TOUCH_PB1_LED_FEEDBACK_ENABLE   ENABLE_THIS_MODULE
#define TCFG_LP_TOUCH_PB1_LED_PORT               IO_PORTC_03
#define TCFG_LP_TOUCH_PB1_LED_ACTIVE_LEVEL       1   // 1 = active level; polarity is inverted — LOW when touched (see FIX-019)

// In-ear detection thresholds
#define TCFG_LP_EARTCH_SOFT_INEAR_VAL            1500
#define TCFG_LP_EARTCH_SOFT_OUTEAR_VAL           800

// CH1 as a key channel (not just ear-detect)
#define TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE  1
#define TCFG_LP_EARTCH_REF_KEY_EVENT_ENABLE      1
```

---

## 7. CTMU Channel Initialization (CH1 vs CH3 — identical after FIX-016)

```
Boot log confirms:
  M2P_CTMU_CH1_CFG0L = 0x0a    (attack time)
  M2P_CTMU_CH1_CFG1L = 0x0f    (sensitivity)
  M2P_CTMU_CH1_CFG2L = 0x45    (threshold)

  M2P_CTMU_CH3_CFG0L = 0x0a    ← identical
  M2P_CTMU_CH3_CFG1L = 0x0f    ← identical
  M2P_CTMU_CH3_CFG2L = 0x45    ← identical
```

Both channels run the same `TouchAlgo_Init` adaptive algorithm. The sensitivity table in `lp_touch_key.c` is also identical for ch1 and ch3.

---

## 8. Fix History Summary

| Fix | What Changed | File |
|---|---|---|
| FIX-015 | Unblocked CH1 event dispatcher and LONG handler | `lp_touch_key.c` |
| FIX-015 | Swapped in-ear/out-ear thresholds (were reversed) | `lp_touch_key.c` |
| FIX-015 | Matched CH1 sensitivity table to CH3 | `lp_touch_key.c` |
| FIX-016 | Cleared `M2P_CTMU_CH_CFG BIT(1)` — EARTCH hw mode OFF | `lp_touch_key.c` |
| FIX-016 | Added `TouchAlgo_Init` + `alog_cfg` for CH1 | `lp_touch_key.c` |
| FIX-016 | Unblocked RAISING handler for CH1 | `lp_touch_key.c` |
| FIX-016 | **PC3 output feature added** (polarity later inverted by FIX-019) | `lp_touch_key.c` |
| FIX-017 | Changed `ch[1].key_value` from `0` → `2` (prevents power-off on HOLD) | `board_jl7016g_hybrid.c` |
| FIX-018 | Added CH1 guard in `__ctmu_notify_key_event()` — PB1 is GPIO-only, all key events suppressed | `lp_touch_key.c` |
| FIX-019 | **PC3 → LOW on FALLING (active-low), HIGH on RAISING / idle** | `lp_touch_key.c` |

---

## Related Documents

- [FIX-015 — PB1 Complete Solution](../FIXING/FIX-015%20—%20PB1_COMPLETE_SOLUTION.md)
- [FIX-016 — PC3 GPIO Touch Feedback](../FIXING/FIX-016%20—%20PB1%20PC3%20GPIO%20Touch%20Feedback.md)
- [FIX-017 — PB1 Hold Power-Off Fix](../FIXING/FIX-017%20—%20PB1%20Hold%20Power-Off%20Fix.md)
- [FIX-018 — PB1 Key Events Suppressed GPIO Only](../FIXING/FIX-018%20—%20PB1%20Key%20Events%20Suppressed%20GPIO%20Only.md)
- [FIX-019 — PC3 Polarity Inverted (Active LOW)](../FIXING/FIX-019%20—%20PC3%20Polarity%20Inverted%20(Active%20LOW).md)
- [PB4 Touch Reference Behavior](../../SDKDOCUMENT/PB4_TOUCH_AND_INEAR_BEHAVIOR.md)
