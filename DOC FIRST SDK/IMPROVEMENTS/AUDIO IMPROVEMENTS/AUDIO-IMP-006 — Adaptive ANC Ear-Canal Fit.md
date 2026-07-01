---
tags: [audio, anc, adaptive, ear-canal, calibration, jl7016g, improvement]
date: 2026-06-08
status: PLANNED — NOT IMPLEMENTED
effort: 🟡 Medium
risk: ⚠️ Requires calibration run per unit — adds production complexity
priority: 11 — Medium effort, high ANC quality improvement
---

# 🔊 AUDIO-IMP-006 — Adaptive ANC Ear-Canal Personalization

> **One-line summary:** Enable the SDK's adaptive ANC mode so each unit calibrates its ANC filter coefficients to the acoustic signature of the individual user's ear canal — the current fixed coefficients are averaged across a population and may under-perform for users with unusual ear geometries.

---

## Current State

Adaptive ANC is **disabled** — fixed coefficients are used:

```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_AUDIO_ANC_EAR_ADAPTIVE_EN    DISABLE
```

The fixed ANC coefficients are stored in flash at:
- `ANCIF_ADR: 0xFD000` — ANC gains (from isd_config.ini)
- `ANCIF1_ADR: 0xFD100` — ANC coefficients

These coefficients were tuned on a reference ear coupler during factory calibration and represent the average ear canal acoustic response. For ears with significantly different volume, shape, or ear-tip seal they produce suboptimal noise cancellation — sometimes the ANC even adds distortion.

---

## What Adaptive ANC Does

When enabled, on each boot (or on user trigger via key press) the system:

1. Plays a known test signal through the DAC into the ear
2. Measures the response with the feedback/error microphone (MIC2)
3. Computes the difference between expected and actual acoustic transfer function
4. Derives personalized FIR filter corrections
5. Stores corrections in RAM (and optionally flash for persistence)

Result: ANC filter is tuned to **this specific user's ear canal** rather than a population average.

```
Boot or calibration trigger
  │
DAC → test tone → ear canal
  │
FB mic (PG7) measures response
  │
DSP: compute personalized correction → write to ANC coefficient RAM
  │
ANC now uses personalized filters until next calibration
```

---

## Recommended Change

```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_AUDIO_ANC_EAR_ADAPTIVE_EN    ENABLE    // was DISABLE
```

### Calibration Trigger Options

The SDK supports multiple calibration trigger modes:

| Mode | Trigger | Best For |
|---|---|---|
| On-ear-insert | Automatic when in-ear detection fires | Consumer product — seamless |
| Key press | User holds key for 3+ seconds | Power user / dev boards |
| App command | RCSP command via BLE app | Mobile app integration |

**Recommended:** On-ear-insert (automatic) — requires in-ear detection to already work correctly. Since FIX-007 through FIX-019 have resolved in-ear detection on this SDK, this trigger is safe to use.

---

## Expected Improvement

| User Ear Type | Fixed Coeff Performance | Adaptive Performance |
|---|---|---|
| Average ear (reference) | ~25 dB NR | ~25–27 dB NR (marginal gain) |
| Larger ear canal | ~15–18 dB NR | ~23–26 dB NR (+8 dB) |
| Loose ear tip fit | ~10–12 dB NR | ~18–20 dB NR (+8 dB) |
| Smaller ear canal | ~20 dB NR | ~25–27 dB NR (+5 dB) |

*NR = Noise Reduction in dB, measured at 1 kHz*

---

## Risk & Trade-offs

| Aspect | Assessment |
|---|---|
| Calibration time per ear | ~1–3 seconds — acceptable |
| Audible test tone | The cal tone is at very low level; most users don't notice |
| Storage | Correction stored in RAM — lost on power cycle unless also flashed (SDK option) |
| In-ear detection dependency | Must confirm FIX-007/010 are deployed; false in-ear detection = cal at wrong time |
| Computation overhead | ~10 ms burst at 96 MHz — negligible |
| Worst case: bad calibration | ANC performance drops; user re-inserts earphone to re-calibrate |
| Reversible | Yes — set `DISABLE`; coefficients revert to fixed factory values |

---

## Verification Steps

1. Enable flag and rebuild
2. Flash to test bud
3. Insert earbud — observe UART log for `adaptive_anc_cal start` / `complete`
4. Compare ANC noise attenuation before and after: hold pink noise source at 40 cm, measure SPL at listener position with/without ANC
5. Re-insert with different ear tip size — confirm new calibration runs and performance adjusts
6. Power cycle — verify calibration either persists (if flash write enabled) or gracefully re-runs on next insert

---

## Related
- [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md) — Section 2
- [→ AUDIO-IMP-003 ANC Right Channel](./AUDIO-IMP-003%20—%20ANC%20Right%20Channel%20Extension.md) — Also requires ANC calibration
- [→ IN-EAR DETECTION](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/IN-EAR%20DETECTION.md) — Trigger dependency
- [→ GUI TAB 07 — ANC Config](../../SDK%20UPDATE%20FIXING/GUI%20DOCUMENTATION/TAB%2007%20—%20ANC%20Config.md)
