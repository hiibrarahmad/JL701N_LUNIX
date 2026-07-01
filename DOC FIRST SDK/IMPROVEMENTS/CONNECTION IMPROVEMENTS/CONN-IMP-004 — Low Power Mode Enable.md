---
tags: [connection, power, low-power, battery, sleep, reconnect, jl7016g, improvement]
date: 2026-06-08
status: PLANNED — TEST RECONNECT LATENCY BEFORE SHIPPING
effort: 🟡 Medium
risk: ⚠️ May increase reconnect time — validate against UX requirement
priority: 12 — Medium effort, significant battery life improvement
---

# 📡 CONN-IMP-004 — Low Power Mode Enable

> **One-line summary:** The system-level low-power mode is currently disabled — the CPU stays at full idle clock (24 MHz) even when no audio is playing. Enabling low power can extend standby battery life by 20–40% at the cost of slightly longer reconnect latency.

---

## Current State

Low power mode is **disabled**:

```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_LOWPOWER_LOWPOWER_SEL    0    // low power mode off
#define TCFG_LOWPOWER_POWER_SEL       PWR_LDO15   // LDO regulator (not buck)
#define TCFG_LOWPOWER_RAM_SIZE        3    // 384 KB RAM retained (3 × 128 KB)
#define TCFG_LOWPOWER_BTOSC_DISABLE   0    // BT oscillator stays on in low power
```

### Current Idle State

When connected but idle (no audio, no user input) the system runs at:
- CPU: 24 MHz
- BT oscillator: ON
- All 384 KB RAM: powered
- LDO15 regulator: always on

This is the highest power idle state — identical to active-connected power draw minus the DSP load.

---

## What Low Power Mode Does

When `TCFG_LOWPOWER_LOWPOWER_SEL = 1`, the SDK transitions to a reduced-power idle:

```
Connected idle → low power state:
  CPU clock: drops from 24 MHz to ~6 MHz (or park state with BT wakeup)
  RAM: only retained segments powered (controlled by TCFG_LOWPOWER_RAM_SIZE)
  Peripheral clocks: gated
  BT oscillator: stays on (BTOSC_DISABLE=0) for connection maintenance
```

The BT connection is maintained throughout — the chip uses the BT wakeup interrupt to return to full power when audio packets arrive or a key is pressed.

---

## LDO vs Buck Consideration

```c
#define TCFG_LOWPOWER_POWER_SEL    PWR_LDO15   // current: LDO regulator
```

At low power states a **switching buck DC-DC converter** is more efficient than the LDO:
- LDO efficiency: ~65–75% at low load
- Buck efficiency: ~85–92% at low load

Switching to buck requires verifying that the PCB has no RF noise issues from the switcher (common concern on BT earphones). See [→ POWER PRIORITY 01](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/POWER%20PRIORITY%2001.md) for the LDO vs Buck analysis for this specific board.

---

## Recommended Change

### Step 1 — Enable low power mode (safe starting point)

```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_LOWPOWER_LOWPOWER_SEL    1    // was 0 — enable low power
// Keep LDO for now; switch to Buck only after RF noise test
#define TCFG_LOWPOWER_POWER_SEL       PWR_LDO15    // unchanged
```

### Step 2 — Test reconnect latency

After enabling, measure:
- Time from in-case (power-off equivalent) → connected and playing audio: target < 3 seconds
- Time from low-power idle → resuming music on phone play: target < 500 ms

### Step 3 — Optionally enable Buck (if RF test passes)

```c
#define TCFG_LOWPOWER_POWER_SEL    PWR_DCDC15   // switch LDO → Buck DC-DC
```

---

## Expected Battery Life Improvement

| State | LDO, Low Power OFF | LDO, Low Power ON | Buck, Low Power ON |
|---|---|---|---|
| Active A2DP (music) | ~8 hours | ~8 hours | ~8 hours |
| Connected idle (no audio) | ~12 hours | ~16–18 hours | ~20–22 hours |
| Standby (case open, connected) | ~15 hours | ~22 hours | ~26 hours |

*Estimates based on 60 mAh cell, 3.7V nominal. Actual values depend on ANC state.*

---

## Risk & Trade-offs

| Aspect | Assessment |
|---|---|
| Reconnect latency increase | +50–200 ms from deep idle — acceptable for most UX |
| ANC resume time | ANC filter reload may add ~100 ms — test carefully |
| TWS sync after low power | Both buds must wake synchronously — verify TWS link maintained |
| Buck RF noise | If switching to Buck: measure BT throughput and audio quality post-switch |
| In-ear detection in low power | CTMU (touch/in-ear) must remain active during low power — verify `TCFG_LP_TOUCH_KEY_ENABLE` still fires wakeup |
| Reversible | Yes — set `TCFG_LOWPOWER_LOWPOWER_SEL=0` to revert |

---

## Verification Steps

1. Enable `TCFG_LOWPOWER_LOWPOWER_SEL=1` and rebuild
2. Flash, pair with phone, play music for 30 seconds
3. Pause music — confirm UART log shows transition to low-power state
4. Resume music on phone — measure time to audio output: must be < 500 ms
5. Remove and re-insert earbud — confirm in-ear detection still wakes from low power
6. Check UART: no `wakeup timeout` or `BT disconnect` messages during idle → low power transitions
7. Measure current draw with multimeter in idle: should drop significantly vs baseline

---

## Related
- [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md) — Section 5
- [→ POWER DEEP DIVE](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/POWER%20DEEP%20DIVE.md)
- [→ POWER PRIORITY 01 — LDO vs Buck](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/POWER%20PRIORITY%2001.md)
- [→ ARCHITECTURE/03-POWER-SYSTEM.md](../../SDK%20UPDATE%20FIXING/ARCHITECTURE/03-POWER-SYSTEM.md)
- [→ CONN-IMP-005 Auto-Shutdown](./CONN-IMP-005%20—%20Auto-Shutdown%20Timer%20Tuning.md) — Works in tandem with low power
