---
tags: [power, ldo, dcdc, buck, p33, ctmu, investigation, boot-loop, root-cause, jl7016g]
date: 2026-06-09
board: JL7016G Hybrid
chip: AC701N (BR28)
status: Closed — LDO confirmed stable, DCDC rejected
result: PWR_LDO15 + LOWPOWER_SEL=1 + VDDIOM_VOL_30V
---

# ⚡ POWER PRIORITY 01b — DCDC Investigation Results and Root Cause

> **This doc is the outcome of the experiment planned in [POWER PRIORITY 01](POWER%20PRIORITY%2001%20%E2%80%94%20LDO%20vs%20Buck%20DC-DC%20on%20JL7016G%20Hybrid.md).  
> Short answer: DCDC cannot be used in current firmware — root cause identified below.**

---

## 1) Hardware Confirmation — Buck Circuit Is Present

Before any firmware change was made, the PCB schematic was reviewed.

Buck circuit confirmed present:

| JL7016G Pin | Net | Connection |
|---|---|---|
| Pin 9 — SW | SW_G8 | L3 (10µH inductor) — one end |
| Pin 13 — DCVDD | DCVDD | L3 other end + C13 (10µF output cap) |
| Pin 8 — PGND | PGND | Switching ground return |
| Pin 10 — VBAT | VBAT | Battery supply to internal switch |

- Inductor: 10µH on DCVDD/SW net — correct value for Jieli BR28 reference design
- Output cap: 10µF present on DCVDD node
- **Verdict: hardware is correctly wired for DCDC operation**

---

## 2) First DCDC Attempt

### Config changed

```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_LOWPOWER_POWER_SEL     PWR_DCDC15   // was PWR_LDO15
#define TCFG_LOWPOWER_LOWPOWER_SEL  1
#define TCFG_LOWPOWER_VDDIOM_LEVEL  VDDIOM_VOL_30V
```

### Result — deterministic boot loop

Boot log showed boot loop triggered at exactly the same point every cycle:

```
[P33] M2P_CTMU_EARTCH_CH = 0x31          ← dual-channel CTMU activation IPC
reset_reason = 0x2                         ← P33_VDDIO_LVD_RST
```

- Crash was deterministic — every boot, same line
- Reset code `0x2` = VDDIO Low Voltage Detect Reset
- Device never reached BT advertising

### Initial hypothesis (incorrect)

LOWPOWER_SEL=1 was causing a power-domain voltage drop during sleep transitions.

---

## 3) Second DCDC Attempt

### Config changed

```c
#define TCFG_LOWPOWER_POWER_SEL     PWR_DCDC15
#define TCFG_LOWPOWER_LOWPOWER_SEL  0            // disabled sleep
#define TCFG_LOWPOWER_VDDIOM_LEVEL  VDDIOM_VOL_28V
```

### Result — same boot loop, LOWPOWER_SEL was not the cause

Boot log again showed identical crash at `M2P_CTMU_EARTCH_CH = 0x31`:

```
reset_reason = 0x2   ← P33_VDDIO_LVD_RST, same as attempt #1
LVD_FLAG = 1
```

One cycle also showed `P33_SOFT_RST` before the LVD reset, confirming the P33 domain was collapsing under load, not during sleep.

---

## 4) Root Cause Analysis

### What `PWR_DCDC15` actually does inside the chip

When `PWR_DCDC15` is selected, it does **two things simultaneously**:

1. Routes DCVDD (1.5V core for MSYS + P11) through the external Buck converter on pin 9/13
2. **Switches the P33 subsystem internal supply from `LDO13` to `DCDC13`** (internal 1.3V buck for P33)

This second effect is the problem.

### P33 domain and CTMU

The P33 subsystem handles:
- CTMU (Capacitive Touch Measurement Unit) — in-ear sensor + reference channel
- RTC + LRC oscillator
- Always-on wake logic

The in-ear detection uses two CTMU channels:
- CH1 → PB1 (in-ear contact pad)
- CH3 → reference pad

When the main CPU sends IPC message `M2P_CTMU_EARTCH_CH = 0x31` (value 0x31 = CH1 + CH3 dual-channel enable), both capacitive sensing channels activate simultaneously. This causes a current surge in the P33 power domain.

### Why it crashes

```
PWR_DCDC15 selected
    → P33 internal supply = DCDC13 (1.3V internal buck)
    → dual-channel CTMU activation (M2P_CTMU_EARTCH_CH = 0x31)
    → instantaneous current spike in P33
    → DCDC13 cannot respond fast enough / insufficient output capacitance
    → P33 VDDIO droops below LVD threshold (2.2V from lvd_con = 0xBD)
    → P33_VDDIO_LVD_RST fires (reset code 0x2)
    → full system reset
    → boot again → same crash → infinite loop
```

The crash is not related to:
- External buck circuit quality
- LOWPOWER_SEL setting
- VDDIOM level
- BTOSC_DISABLE setting

It is caused by the internal P33 DCDC13 supply being unable to absorb the dual-channel CTMU activation surge.

### Why `CONFIG_VDDIO_LVD_LEVEL` didn't help

`CONFIG_VDDIO_LVD_LEVEL` is **commented out on all Jieli reference boards**. The active threshold comes from the OTP `lvd_con = 0xBD` register, which sets the VDDIO LVD threshold to 2.2V. Changing firmware flags cannot override this without changing the OTP value — which is not a safe path.

---

## 5) Hardware Fix Path (not implemented — future option)

The DCDC crash can potentially be resolved at hardware level:

**Add 100µF+ bulk capacitor on VBAT (pin 10)**

- Adds energy storage close to the chip
- Reduces instantaneous VBAT droop when P33 DCDC13 switches under load
- Gives P33 DCDC13 enough headroom to absorb the CTMU activation surge without tripping LVD

**Why not implemented now:**
- Requires PCB modification (adds component, may need layout space)
- Not a zero-risk change — needs validation of audio/RF noise after adding bulk cap
- LDO path already gives full functionality at cost of ~2–4mA

---

## 6) Final Stable Configuration

```c
// board_jl7016g_hybrid_cfg.h — FINAL (confirmed stable)
#define TCFG_LOWPOWER_POWER_SEL     PWR_LDO15        // DCDC disabled — see root cause above
#define TCFG_LOWPOWER_BTOSC_DISABLE 0
#define TCFG_LOWPOWER_LOWPOWER_SEL  1                // BT+CPU idle sleep ENABLED
#define TCFG_LOWPOWER_VDDIOM_LEVEL  VDDIOM_VOL_30V
```

### What LOWPOWER_SEL=1 gives on LDO

Even without DCDC, enabling `LOWPOWER_SEL=1` provides real power savings:

- When BT stack goes idle (between activity events), system clock gates down from 48MHz → LRC (~32kHz)
- Typical idle current saving: **2–4mA average**
- No impact on functionality — BT stack wakes normally for connections, audio, key events
- Boot log confirmed clean: full boot sequence → power-on tone → BT advertising → TWS page scan

### Confirmed stable boot log signature (with LDO + LOWPOWER_SEL=1)

```
reset_reason = 0x1   ← P33_SOFT_RST (normal power-on)
[P33] M2P_CTMU_EARTCH_CH = 0x31   ← dual-channel in-ear ENABLED
... (no crash)
[BT] ADV start
[TWS] page scan active
```

---

## 7) Power Comparison Summary

| Config | DCVDD mode | LOWPOWER_SEL | Status | Current saved |
|---|---|---|---|---|
| PWR_LDO15 + SEL=0 | Linear | No sleep | Previous baseline | 0 |
| PWR_DCDC15 + SEL=1 | Buck | Sleep | **CRASH — boot loop** | N/A |
| PWR_DCDC15 + SEL=0 | Buck | No sleep | **CRASH — boot loop** | N/A |
| PWR_LDO15 + SEL=1 | Linear | Sleep | **STABLE ✅** | ~2–4mA idle avg |

---

## 8) Decision

| Question | Answer |
|---|---|
| Is DCDC firmware-switchable? | No — P33 DCDC13 collapses under dual-channel CTMU |
| Does hardware need to change for DCDC? | Yes — 100µF+ VBAT bulk cap minimum |
| Is LDO the correct current config? | Yes |
| Is LOWPOWER_SEL=1 safe on LDO? | Yes — confirmed stable, saves 2–4mA |
| Should DCDC ever be revisited? | Yes — after adding VBAT bulk cap and re-validating |

---

## 9) Related Documents

- [→ POWER PRIORITY 01 — Theory and planning](POWER%20PRIORITY%2001%20%E2%80%94%20LDO%20vs%20Buck%20DC-DC%20on%20JL7016G%20Hybrid.md)
- [→ POWER DEEP DIVE — Charging Wake, Low Power, and Reconnect Latency](POWER%20DEEP%20DIVE%20%E2%80%94%20Charging%20Wake%2C%20Low%20Power%2C%20and%20Reconnect%20Latency.md)
- [→ IN-EAR DETECTION — CTMU Capacitive Sensing](IN-EAR%20DETECTION%20%E2%80%94%20CTMU%20Capacitive%20Sensing%2C%20GPIO%20Mapping%2C%20State%20Machine.md)
- [→ Boot Log 08 — BOOT LOOP EXCEPTION LOG](../BOOT%20LOG%20DEEP%20ANALYSIS/08%20-%20BOOT%20LOOP%20EXCEPTION%20LOG%20-%20ANC%20Init%20Crash%20and%20Recovery.md)
