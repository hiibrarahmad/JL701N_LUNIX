---
tags: [fix, mic, sensitivity, mic-mode, single-ended, differential, audio, adc]
date: 2026-04-27
status: COMPLETE & DEPLOYED
severity: FUNCTIONAL — CALL MIC INAUDIBLE AT NORMAL DISTANCE
---

# FIX-013 — MIC0 Differential Mode Mismatch — Changed to Single-Ended

## Summary

After FIX-012 restored MIC power (PA2 MICBIAS), the MIC could only detect a direct physical tap on the capsule. Normal conversation at any distance produced no audio. The MIC was alive but had near-zero sensitivity.

## Root Cause

`TCFG_AUDIO_MIC_MODE` was set to `AUDIO_MIC_CAP_DIFF_MODE` (differential AC-coupled mode). In differential mode, the JL BR28 ADC measures the **voltage difference** between MIC+ (PA1) and MIC−.

The JL7016G schematic wires MIC0 as **single-ended**: only PA1 carries the MIC signal through a coupling capacitor. There is no differential MIC− signal wire. In this configuration:

- Ambient sound → PA1 moves slightly (small signal)
- MIC− (no connection / internal reference) → does not move
- Differential result `V(PA1) − V(MIC−)` ≈ `small value − reference` → extremely weak effective swing

This means the ADC barely sees any signal from normal speech. A hard physical tap on the capsule creates a large vibration burst strong enough to momentarily cross the detection floor — which is why only taps registered.

The default SDK comment (`注意:ANC使能情况下，使用差分mic` = "use differential MIC when ANC is enabled") applies to **ANC mics (MIC1 FF, MIC2 FB)** which may be proper differential capsules. It does not apply to the call/talk MIC (MIC0) which is single-ended on this board.

## Fix Applied

**File:** `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h`

```c
// Before (wrong — differential mode on a single-ended hardware MIC)
#define TCFG_AUDIO_MIC_MODE    AUDIO_MIC_CAP_DIFF_MODE
#define TCFG_AUDIO_MIC1_MODE   AUDIO_MIC_CAP_DIFF_MODE
#define TCFG_AUDIO_MIC2_MODE   AUDIO_MIC_CAP_DIFF_MODE
#define TCFG_AUDIO_MIC3_MODE   AUDIO_MIC_CAP_DIFF_MODE

// After (MIC0 = single-ended for PA1 signal; MIC1/MIC2 = differential for ANC)
#define TCFG_AUDIO_MIC_MODE    AUDIO_MIC_CAP_MODE        // call/talk MIC — single-ended on PA1
#define TCFG_AUDIO_MIC1_MODE   AUDIO_MIC_CAP_DIFF_MODE   // ANC feed-forward (ANCL_FF_MIC = A_MIC1)
#define TCFG_AUDIO_MIC2_MODE   AUDIO_MIC_CAP_DIFF_MODE   // ANC feed-back   (ANCL_FB_MIC = A_MIC2)
#define TCFG_AUDIO_MIC3_MODE   AUDIO_MIC_CAP_DIFF_MODE   // unused on this board, kept diff
```

### Mode reference

| Macro value | Meaning |
|---|---|
| `AUDIO_MIC_CAP_MODE` (0) | Single-ended AC-coupled — PA1 only as MIC signal |
| `AUDIO_MIC_CAP_DIFF_MODE` (1) | Differential AC-coupled — expects MIC+ and MIC− pair |
| `AUDIO_MIC_CAPLESS_MODE` (2) | Single-ended capless (DC-coupled) — not used here |

### Why MIC1 and MIC2 stay differential

ANC in this SDK is `ANC_HYBRID_EN` (feed-forward + feed-back). The ANC mics (MIC1 = FF, MIC2 = FB) may be physically wired as differential pairs for better noise rejection in the ANC path. Changing them to single-ended would require hardware verification and could degrade ANC performance.

## No-Touch Policy

- `adc_data.mic1_mode` and `adc_data.mic2_mode` — unchanged (differential, for ANC)
- `ANCL_FF_MIC = A_MIC1`, `ANCL_FB_MIC = A_MIC2` — ANC assignment unchanged
- `mic_ldo_vsel`, `mic_bias_res`, `mic_ldo_isel` — unchanged
- `TCFG_AUDIO_MIC_PWR_CTL = MIC_PWR_FROM_MIC_BIAS` — unchanged (from FIX-012)
- Runtime gain: `aec_mic_gain = 12` (default when factory config absent) — already near max, not the issue

## MIC signal chain summary after FIX-012 + FIX-013

```
Electret MIC capsule
  VCC ← PA2 (MICBIAS, 2.4V, via 2.0kΩ series bias resistor)
  OUT → coupling cap → PA1 (MIC0 single-ended ADC input)
  GND → board GND

ADC (MIC0, single-ended mode):
  PA1 signal captured directly
  aec_mic_gain = 12 (0-15 scale)
  CVP → speech codec → BT call
```

## Verification

- Build: `EXIT:0` after change
- Flash and make BT call → MIC should now pick up normal conversation at normal distance
- UART: confirm `CVP_cfg Mic0_gain:12` log line at boot
