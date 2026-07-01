---
tags: [audio, anc, wind-noise, detection, jl7016g, improvement]
date: 2026-06-08
status: PLANNED — NOT IMPLEMENTED
effort: 🟢 Low
risk: ✅ Safe — software flag only
priority: ⭐ 2 — High impact for outdoor users
---

# 🔊 AUDIO-IMP-004 — Wind Noise Detection

> **One-line summary:** Enable the SDK's built-in wind noise detector so ANC is automatically softened when the feedforward mic detects turbulent airflow — prevents the characteristic ANC "wind rumble" artifact outdoors.

---

## Current State

Wind noise detection is **disabled**:

```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_AUDIO_ANC_WIND_NOISE_DET_ENABLE    DISABLE
```

### The Problem Without Wind Detection

Hybrid ANC feedforward microphones are extremely sensitive to low-frequency pressure variations. When wind flows across the outer mic (ANCL_FF_MIC = A_MIC1 on PA4) the signal has a characteristic low-frequency burst that the ANC DSP interprets as "noise to cancel."

The result: instead of cancelling the wind noise, the ANC **amplifies** a pumping/booming artifact. Users typically turn ANC off when walking outdoors or cycling — defeating the entire ANC system.

---

## What Wind Noise Detection Does

The SDK's wind noise detector runs a spectral analysis on the feedforward mic signal:

```
FF Mic signal → spectral shape classifier → is it wind turbulence?
                                                    │
                                        YES ────────▼
                                              Reduce FF mic gain
                                              Blend toward FB-only mode
                                              (or fully disable ANC)
                                        NO  → normal ANC operation
```

When wind is detected, the system automatically transitions from **Hybrid FF+FB** to a **feedback-only** (or attenuated FF) mode, which is less sensitive to wind turbulence.

---

## Recommended Change

```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_AUDIO_ANC_WIND_NOISE_DET_ENABLE    ENABLE    // was DISABLE
```

No other changes required. The wind noise classifier threshold and response speed are configured via the AC701N Config GUI (TAB 07 — ANC Config) after enabling.

### Recommended GUI settings after enabling

| Parameter | Suggested Start Value | Notes |
|---|---|---|
| Wind detection sensitivity | Medium | Too high = false positives while running; too low = misses real wind |
| Response speed | Fast (< 100 ms) | Wind bursts are sudden |
| FF attenuation on wind | -12 dB | Gradual — avoids audible transition click |

---

## Risk & Trade-offs

| Aspect | Assessment |
|---|---|
| False positives (non-wind) | Low at medium sensitivity — loud bass in music rarely triggers it |
| ANC performance reduction when triggered | Intentional — FB-only ANC still provides ~10–15 dB NR vs 25+ dB hybrid |
| Transition audibility | Should be inaudible at -12 dB/step; tune in GUI |
| CPU overhead | < 1 MHz extra — runs in ANC DSP interrupt context |
| Reversible | Yes — `DISABLE` to revert |

---

## Verification Steps

1. Enable flag and rebuild
2. Flash to test bud
3. **Outdoor test:** Walk quickly while wearing — confirm no wind pumping artifact
4. **Indoor test:** Play music with strong bass — confirm ANC remains in hybrid mode (no false trigger)
5. Enable UART log and confirm `wind_det` state transitions print when blowing on mic
6. Compare ANC noise attenuation: indoors (hybrid, full performance) vs outdoors in wind (FB-only, graceful degradation)

---

## Related
- [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md) — Section 2
- [→ AUDIO-IMP-003 ANC Right Channel](./AUDIO-IMP-003%20—%20ANC%20Right%20Channel%20Extension.md) — Enable simultaneously with right-channel ANC
- [→ GUI TAB 07 — ANC Config](../../SDK%20UPDATE%20FIXING/GUI%20DOCUMENTATION/TAB%2007%20—%20ANC%20Config.md)
