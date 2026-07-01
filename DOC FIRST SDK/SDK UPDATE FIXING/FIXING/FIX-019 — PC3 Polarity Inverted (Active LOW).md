---
tags: [fix, gpio, pc3, polarity, pb1, active-low, ctmu]
date: 2026-05-04
status: COMPLETE & DEPLOYED
severity: CHANGE — Inverted PC3 output polarity (active-HIGH → active-LOW)
files_changed: [cpu/br28/lp_touch_key.c]
---

# FIX-019: PC3 GPIO Output Polarity Inverted (Active-LOW)

**Status:** COMPLETE & DEPLOYED  
**Build:** SUCCESS (0 errors, ota.bin generated)  
**Date:** May 4, 2026  

---

## Change Request

The PC3 output logic from FIX-016 drove PC3 **HIGH** while PB1 was touched and **LOW** on release (active-HIGH). The hardware downstream of PC3 required the opposite: **LOW** while touched and **HIGH** on release (active-LOW).

---

## Before (FIX-016 — active-HIGH)

| PB1 State | CTMU Event | PC3 |
|---|---|---|
| Idle / boot | — | LOW |
| Finger DOWN | FALLING | **HIGH** |
| Finger UP | RAISING | LOW |

---

## After (FIX-019 — active-LOW)

| PB1 State | CTMU Event | PC3 |
|---|---|---|
| Idle / boot | — | **HIGH** |
| Finger DOWN | FALLING | **LOW** |
| Finger UP | RAISING | HIGH |

---

## Code Changes

**File:** `cpu/br28/lp_touch_key.c`

### 1. Init — idle state changed from LOW to HIGH

```c
// Before (FIX-016):
gpio_write(TCFG_LP_TOUCH_PB1_LED_PORT, !TCFG_LP_TOUCH_PB1_LED_ACTIVE_LEVEL); /* idle LOW */

// After (FIX-019):
gpio_write(TCFG_LP_TOUCH_PB1_LED_PORT, TCFG_LP_TOUCH_PB1_LED_ACTIVE_LEVEL); /* idle HIGH */
```

### 2. FALLING handler — drive LOW on touch down

```c
// Before (FIX-016):
// CH1 (PB1) touch active: drive PC3 HIGH
gpio_write(TCFG_LP_TOUCH_PB1_LED_PORT, TCFG_LP_TOUCH_PB1_LED_ACTIVE_LEVEL);

// After (FIX-019):
// CH1 (PB1) touch active: drive PC3 LOW
gpio_write(TCFG_LP_TOUCH_PB1_LED_PORT, !TCFG_LP_TOUCH_PB1_LED_ACTIVE_LEVEL);
```

### 3. RAISING handler — drive HIGH on release

```c
// Before (FIX-016):
// CH1 (PB1) touch released: drive PC3 LOW
gpio_write(TCFG_LP_TOUCH_PB1_LED_PORT, !TCFG_LP_TOUCH_PB1_LED_ACTIVE_LEVEL);

// After (FIX-019):
// CH1 (PB1) touch released: drive PC3 HIGH
gpio_write(TCFG_LP_TOUCH_PB1_LED_PORT, TCFG_LP_TOUCH_PB1_LED_ACTIVE_LEVEL);
```

---

## Why Not Just Change ACTIVE_LEVEL?

`TCFG_LP_TOUCH_PB1_LED_ACTIVE_LEVEL` is defined as `1` in `board_jl7016g_hybrid_cfg.h`. Changing it to `0` would achieve the same result without touching `lp_touch_key.c`. Both approaches are valid. The direct code change was chosen here because it is immediately visible in the driver source without needing to trace the config macro.

If you want to change polarity via config in future: set `TCFG_LP_TOUCH_PB1_LED_ACTIVE_LEVEL 0`.

---

## Timing (after FIX-019)

```
Boot
  └─ PC3 = HIGH (idle)

Finger touches PB1
  └─ CTMU FALLING → gpio_write(PC3, LOW)   PC3 = LOW  ◄─── active state

Finger held
  └─ PC3 stays LOW for entire touch duration

Finger lifts
  └─ CTMU RAISING → gpio_write(PC3, HIGH)  PC3 = HIGH ◄─── idle state
```

---

## Verification

With oscilloscope or logic analyzer on PC3:
- **Idle:** 3.3 V (HIGH)
- **Touch PB1:** drops to 0 V within ~200 µs of finger contact
- **Release PB1:** returns to 3.3 V within ~200 µs of lift

---

## Related Documents

- [FIX-016 — PB1 PC3 GPIO Touch Feedback](./FIX-016%20—%20PB1%20PC3%20GPIO%20Touch%20Feedback.md) — original PC3 feature
- [01-TOUCH-SYSTEM.md](../ARCHITECTURE/01-TOUCH-SYSTEM.md) — updated system overview
