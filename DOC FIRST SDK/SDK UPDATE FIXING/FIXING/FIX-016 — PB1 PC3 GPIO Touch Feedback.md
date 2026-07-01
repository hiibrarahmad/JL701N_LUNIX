---
tags: [fix, gpio, pb1, pc3, touch-feedback, ctmu, falling, raising]
date: 2026-05-01
status: COMPLETE & DEPLOYED
severity: FEATURE — GPIO output mirrors PB1 touch state in real time
files_changed: [cpu/br28/lp_touch_key.c, apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h]
---

# FIX-016: PB1 PC3 GPIO Touch Feedback + CH1 Blocking Points

**Status:** COMPLETE & DEPLOYED
**Build:** SUCCESS (0 errors, ota.bin generated)
**Date:** May 1, 2026

---

## Part A — Three CH1 Blocking Points (root-cause fixes required before Part B)

Before the PC3 GPIO output would be meaningful, CH1 had three silent blockers preventing any FALLING/RAISING events from reaching the handler. These had to be resolved first.

### Block 1 — EARTCH Hardware Mode Left ON (`M2P_CTMU_CH_CFG BIT(1)`)

**File:** `cpu/br28/lp_touch_key.c` — init section

**Problem:** An unconditional `M2P_CTMU_CH_CFG |= BIT(1)` was setting the hardware EARTCH capture mode for CH1 even when CH1 was configured as a normal key channel. This kept the CTMU hardware in an exclusive ear-detect state and suppressed all software FALLING/RAISING events for CH1.

**Fix:**
```c
// Before — always executed:
M2P_CTMU_CH_CFG |= BIT(1);

// After — only when CH1 is NOT a key:
#if !TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE
M2P_CTMU_CH_CFG |= BIT(1);
#endif
```

**Boot log proof:**
```
M2P_CTMU_CH_CFG = 0x0   ← 0 = hardware EARTCH mode OFF (correct)
```

---

### Block 2 — CH1 Missing `TouchAlgo_Init` (adaptive algorithm not running)

**File:** `cpu/br28/lp_touch_key.c` — init section, CH1 EARTCH branch

**Problem:** The init loop had a branch for `eartch_ch` (CH1) that called `TouchAlgo_Init` only for CH3. CH1 was initialised without the adaptive cfg2 algorithm, so the CTMU could not dynamically adjust its threshold, causing persistent false readings.

**Fix:** Added `TouchAlgo_Init` + full `alog_cfg` setup for CH1 inside a `#if TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE` guard:

```c
#if TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE
    // CH1 — init adaptive algorithm exactly like CH3
    alog_cfg.ch = 1;
    alog_cfg.cfg2_h = &M2P_CTMU_CH1_CFG2H;
    alog_cfg.cfg2_l = &M2P_CTMU_CH1_CFG2L;
    TouchAlgo_Init(&alog_cfg);
#endif
```

**Boot log proof:**
```
CH1 key init: read vm alog cfg
M2P_CTMU_CH1_CFG2H = 0x0
M2P_CTMU_CH1_CFG2L = 0x45
M2P_CTMU_CH1_CFG1H = 0x0
M2P_CTMU_CH1_CFG1L = 0xf
M2P_CTMU_CH1_CFG0H = 0x0
M2P_CTMU_CH1_CFG0L = 0xa
```

---

### Block 3 — RAISING Handler Intercepted by EARTCH Ear-Out Logic

**File:** `cpu/br28/lp_touch_key.c` — CTMU_P2M_CH1_RAISING_EVENT handler

**Problem:** An unconditional block inside the RAISING handler was checking if `ch_num == eartch_ch` (which is CH1) and routing CH1 RAISING events directly to `ctmu_eartch_event_handle(LP_EARTCH_EVENT_OUT_STATE)` before they could reach `ctmu_raise_click_handle()`. This silently cancelled every RAISING event for CH1, so SHORT/DOUBLE/HOLD_UP events were never generated.

**Fix:** Wrapped the intercept with a flag:
```c
#if !TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE
    if (__this->config->eartch_en && (__this->config->eartch_ch == ch_num)) {
        if (__this->eartch_inear_ok) {
            ctmu_eartch_event_handle(LP_EARTCH_EVENT_OUT_STATE);
        }
        break;
    }
#endif
```

**Boot log proof:** After this fix, `CH1: RAISING` appears in logs and is followed by `notify key1 short event`.

---

## Part B — PC3 GPIO Output (the actual feature)

### What It Does

PC3 (IO_PORTC_03) is a GPIO output that mirrors the raw capacitive state of PB1:

| PB1 State   | CTMU Event | PC3 Output   |
| ----------- | ---------- | ------------ |
| Finger DOWN | FALLING    | **LOW (0)**  |
| Finger UP   | RAISING    | **HIGH (1)** |

> **Note (FIX-019):** Original polarity was HIGH on touch, LOW on release. Polarity was inverted in FIX-019 to active-LOW to match downstream hardware. Idle/boot state is HIGH.

### Why FALLING/RAISING (not key events)

Key events (SHORT, LONG, HOLD) are fired by software timers that start on FALLING and expire after 300 ms / 2000 ms respectively. If PC3 were controlled from key events:
- PC3 would be delayed ~300 ms on every touch
- PC3 would go HIGH multiple times per hold (one per HOLD repeat)
- PC3 would miss the release if the finger lifted before SHORT timeout

FALLING/RAISING are the raw hardware edge signals — they give exact, jitter-free state.

### Code (cpu/br28/lp_touch_key.c)

```c
// ── FALLING: finger touches PB1 → PC3 LOW ───────────────────────────
case CTMU_P2M_CH0_FALLING_EVENT:
case CTMU_P2M_CH1_FALLING_EVENT:
case CTMU_P2M_CH2_FALLING_EVENT:
case CTMU_P2M_CH3_FALLING_EVENT:
case CTMU_P2M_CH4_FALLING_EVENT:
    log_debug("CH%d: FALLING", ch_num);
    is_lpkey_active = 1;

#if TCFG_LP_TOUCH_PB1_LED_FEEDBACK_ENABLE
    // CH1 (PB1) touch active: drive PC3 LOW
    if (ch_num == 1) {
        gpio_write(TCFG_LP_TOUCH_PB1_LED_PORT, !TCFG_LP_TOUCH_PB1_LED_ACTIVE_LEVEL);
    }
#endif
    break;

// ── RAISING: finger leaves PB1 → PC3 HIGH ───────────────────────────
case CTMU_P2M_CH0_RAISING_EVENT:
case CTMU_P2M_CH1_RAISING_EVENT:
case CTMU_P2M_CH2_RAISING_EVENT:
case CTMU_P2M_CH3_RAISING_EVENT:
case CTMU_P2M_CH4_RAISING_EVENT:
    log_debug("CH%d: RAISING", ch_num);
    is_lpkey_active = 0;

#if TCFG_LP_TOUCH_PB1_LED_FEEDBACK_ENABLE
    // CH1 (PB1) touch released: drive PC3 HIGH
    if (ch_num == 1) {
        gpio_write(TCFG_LP_TOUCH_PB1_LED_PORT, TCFG_LP_TOUCH_PB1_LED_ACTIVE_LEVEL);
    }
#endif
```

### Configuration (board_jl7016g_hybrid_cfg.h)

```c
// Enable the PC3 output feature
#define TCFG_LP_TOUCH_PB1_LED_FEEDBACK_ENABLE   ENABLE_THIS_MODULE

// Which GPIO pin to drive
#define TCFG_LP_TOUCH_PB1_LED_PORT               IO_PORTC_03

// 1 = HIGH when touched, 0 = LOW when touched
#define TCFG_LP_TOUCH_PB1_LED_ACTIVE_LEVEL       1
```

To disable: set `TCFG_LP_TOUCH_PB1_LED_FEEDBACK_ENABLE 0` — no GPIO writes occur, zero overhead.

To change the pin: update `TCFG_LP_TOUCH_PB1_LED_PORT` to any valid `IO_PORTx_xx` constant.

To invert polarity: change `TCFG_LP_TOUCH_PB1_LED_ACTIVE_LEVEL` to `0`.

---

## Timing

```
Finger contact
     │
     ▼ ~50 µs
CTMU threshold crossed
     │
     ▼ ~100 µs
CTMU_P2M_CH1_FALLING_EVENT fires
     │
     ▼ < 500 ns
gpio_write(IO_PORTC_03, 1) executes
     │
     ▼
PC3 = HIGH  ←─── stays here ────────────────────────────────────┐
                                                                  │
Finger lifts                                                      │
     │                                                            │
     ▼ ~50 µs                                                     │
CTMU threshold crossed back                                       │
     │                                                            │
     ▼ ~100 µs                                                    │
CTMU_P2M_CH1_RAISING_EVENT fires ────────────────────────────────┘
     │
     ▼ < 500 ns
gpio_write(IO_PORTC_03, 0) executes
     │
     ▼
PC3 = LOW
```

---

## Boot Log Validation

After all three blocking points are fixed and the PC3 code is in place, boot log shows:

```
[LP_KEY]CH1 key init: read vm alog cfg    ← Block 2 fixed
M2P_CTMU_CH_CFG = 0x0                     ← Block 1 fixed

[LP_KEY]CH1: FALLING                      ← FALLING fires
[LP_KEY]CH1: RAISING                      ← RAISING fires (Block 3 fixed)
[LP_KEY]notify key1 short event, cnt: 1   ← key events flow through
[KEY_EVENT_DEAL]key_event:12 0 0          ← application receives event
```

---

## Related Documents

- [01-TOUCH-SYSTEM.md](../ARCHITECTURE/01-TOUCH-SYSTEM.md) — Full system architecture
- [FIX-015 — PB1 Complete Solution](./FIX-015%20—%20PB1_COMPLETE_SOLUTION.md) — Earlier CH1 unblocking work
- [FIX-017 — PB1 Hold Power-Off Fix](./FIX-017%20—%20PB1%20Hold%20Power-Off%20Fix.md) — key_value fix that followed
- [FIX-019 — PC3 Polarity Inverted (Active LOW)](./FIX-019%20—%20PC3%20Polarity%20Inverted%20(Active%20LOW).md) — polarity reversed after this fix
