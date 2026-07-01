---
tags: [fix, mic, power, pa0, pa2, micbias, audio]
date: 2026-04-27
status: COMPLETE & DEPLOYED
severity: HARDWARE BRING-UP BLOCKER
---

# FIX-012 — MIC Power PA0 Unconnected — Switched to PA2 MICBIAS

## Summary

Main microphone produced zero audio. Hardware was alive (MIC capsule present, wired to PA1 and PA2) but the ADC received no signal at all. The MIC capsule had no power supply.

## Root Cause

`TCFG_AUDIO_MIC_PWR_CTL` was set to `MIC_PWR_FROM_MIC_LDO`, which routes the internal LDO voltage output to **PA0**. In the JL7016G schematic, **PA0 is not connected** to the MIC circuit. The MIC capsule had no VCC/bias supply and therefore produced no signal.

The schematic has:
- **PA1** → MIC signal input (through coupling cap)
- **PA2** → MICBIAS output (MIC capsule VCC/bias)
- **PA0** → floating / not connected to MIC

Another SDK that worked on the same hardware used `MIC_PWR_FROM_MIC_BIAS`, which routes the internal MICBIAS voltage to **PA2** — the pin that IS connected in the schematic.

## Fix Applied

**File:** `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h`

```c
// Before (broken — PA0 not wired in schematic)
#define TCFG_AUDIO_MIC_PWR_CTL    MIC_PWR_FROM_MIC_LDO

// After (fix — PA2 IS wired to MIC VCC in schematic)
#define TCFG_AUDIO_MIC_PWR_CTL    MIC_PWR_FROM_MIC_BIAS
```

### Cascade (automatic — driven by existing `#if` blocks in cfg.h)

| Macro | Before | After | Effect |
|---|---|---|---|
| `TCFG_AUDIO_MIC0_BIAS_EN` | undefined (0) | `ENABLE_THIS_MOUDLE` | PA2 MICBIAS output active |
| `TCFG_AUDIO_MIC_LDO_EN` | `ENABLE_THIS_MOUDLE` | undefined (falls to 0) | PA0 LDO output disabled |
| `adc_data.mic_bias_inside` | 0 | 1 | Internal bias circuit on |
| `adc_data.mic_ldo_pwr` | 1 | 0 | LDO output to PA0 off |

### MIC bias parameters in effect (board_jl7016g_hybrid.c, unchanged)

| Field | Value | Meaning |
|---|---|---|
| `mic_ldo_vsel` | 5 | 2.4V MICBIAS output voltage |
| `mic_bias_res` | 4 | 2.0kΩ series bias resistor |
| `mic_ldo_isel` | 3 | 2.5µA LDO quiescent current |

## No-Touch Policy

- `adc_data` struct in `board_jl7016g_hybrid.c` — no changes (auto-driven by `#ifndef` guards)
- ANC MIC assignments (`ANCL_FF_MIC = A_MIC1`, `ANCL_FB_MIC = A_MIC2`) — unrelated, unchanged
- MIC mode — unchanged at this step (see FIX-013 for sensitivity follow-up)

## Verification

- MIC now picks up audio (confirmed: capsule responds to direct tap/touch)
- Build: `EXIT:0` after change
- Next issue identified: sensitivity too low for normal speech — see FIX-013
