---
tags: [audio, microphone, gain, anc, call, optimization, jl7016g, improvement]
date: 2026-06-08
status: PLANNED — TUNING REQUIRED
effort: 🟢 Low
risk: ✅ Safe — runtime tunable via GUI, no build required
priority: 6 — Low effort, direct impact on call quality and ANC
---

# 🎙️ AUDIO-IMP-009 — MIC Gain Optimization

> **One-line summary:** The current MIC gain values are factory defaults — the ANC feedback mic is at 0 dB (possibly too low for good error signal), the call mic is at 13 dB (possibly too high causing saturation). Systematic tuning improves both ANC depth and call voice clarity.

---

## Current Gain Values

From `user_cfg.c` — read from `syscfg_read(CFG_AEC_ID, &aec_cfg)`:

| Microphone | Role | Current Gain | Pin |
|---|---|---|---|
| MIC0 (`talk_mic_gain`) | Call / uplink voice | **13 dB** | PA1 (ADC, single-ended) |
| MIC1 (`ff_mic_gain`) | ANC Feedforward (FF) | **13 dB** | PA4 (MICBIAS1, differential) |
| MIC2 (`fb_mic_gain`) | ANC Feedback/Error (FB) | **0 dB** | PG7 (MICBIAS2, differential) |
| DAC analog gain | Output level | **12** (index) | — |

---

## Problem Analysis

### MIC2 (ANC Feedback) at 0 dB — Likely Too Low

The feedback/error microphone measures the **residual noise** inside the ear canal after ANC processing. This signal drives the ANC control loop. If it is too weak:
- The ANC loop has insufficient error signal to converge
- ANC performance suffers — residual noise is not fully cancelled
- The adaptive ANC (AUDIO-IMP-006) would also fail to calibrate correctly

**0 dB gain on a MEMS microphone (ZTS6216, SNR = 65 dB) may not be enough to overcome the noise floor at low residual signal levels.**

Recommended starting point: **6–12 dB for the FB mic**.

### MIC0 (Call) at 13 dB — May Cause Saturation in Loud Environments

In a noisy room or outdoors:
- Loud ambient noise + high mic gain = ADC saturation → clipping in the call uplink
- The DNN denoiser (CVP_DNS_MODE) runs after the ADC, so saturated input cannot be recovered
- Remote callers hear distorted, clipped audio

Recommended range: **6–10 dB for the call mic** when using DNN denoiser (which provides its own gain riding).

### MIC1 (ANC Feedforward) at 13 dB — May Clip on Loud Noise

The FF mic faces outside — it captures environmental noise. At 13 dB in a loud environment (above ~90 dB SPL) it may saturate, feeding corrupted noise signal to the ANC DSP and generating artifacts.

Recommended range: **8–12 dB for FF mic** depending on target noise environment.

---

## Where to Change These Values

### Method 1 — AC701N GUI Tool (Recommended, No Rebuild)

- Open **TAB 04 — Microphone Config**
- Adjust: Talk Mic Gain, FF Mic Gain, FB Mic Gain
- Click **Write** to update the syscfg flash region (non-firmware write)
- Changes take effect on next boot

### Method 2 — Direct Config in user_cfg.c (Code Change)

```c
// apps/earphone/user_cfg.c — inside syscfg_read(CFG_AEC_ID) fallback defaults
aec_cfg.talk_mic_gain   = 8;    // was 13 — reduce to prevent saturation
aec_cfg.ff_mic_gain     = 10;   // was 13 — moderate outdoor noise environment
aec_cfg.fb_mic_gain     = 8;    // was 0  — raise to get usable error signal
aec_cfg.dac_analog_gain = 12;   // keep (DAC output level, not input)
```

---

## Recommended Tuning Procedure

### Call MIC0 Tuning
1. Place in a room with moderate background noise (TV at low level)
2. Make a call to a second phone
3. On the receiving phone, note if voice is: too quiet, clear, or distorted/clipped
4. If clipped → lower `talk_mic_gain` by 2 dB and retry
5. If too quiet → raise by 2 dB and retry
6. Target: voice is clearly audible, no clipping during normal conversation volume

### ANC FF MIC1 Tuning
1. Enable ANC, play known noise (pink noise via speaker at ~70 dB SPL at 40 cm)
2. Monitor UART log for ANC stability messages
3. If ANC oscillates or makes artifact → lower `ff_mic_gain`
4. If ANC performance is poor → raise `ff_mic_gain` slightly
5. Target: stable ANC with no audible artifacts

### ANC FB MIC2 Tuning
1. With ANC active, insert bud and check residual noise (listen for low-frequency noise leakthrough)
2. Raise `fb_mic_gain` from 0 to 6 dB first
3. If ANC improves → try 8–12 dB
4. If ANC becomes unstable (oscillation/howling) → lower gain
5. Target: error signal strong enough for the loop to converge without instability

---

## Recommended Starting Values (From Analysis)

| MIC | Current | Recommended Start | Rationale |
|---|---|---|---|
| MIC0 call | 13 dB | **8 dB** | DNN provides gain riding; 13 saturates outdoors |
| MIC1 FF | 13 dB | **10 dB** | Slight reduction for headroom on loud noise events |
| MIC2 FB | 0 dB | **8 dB** | Raise to get adequate error signal for ANC loop |
| DAC analog | 12 | **12** (no change) | Output level is fine |

---

## Risk & Trade-offs

| Aspect | Assessment |
|---|---|
| Call too quiet if lowered too much | Listen test verifies |
| ANC loop instability if FB too high | Distinctive howling — easy to detect, lower gain |
| Production repeatability | GUI tool values stored in syscfg region — not in firmware binary |
| Reversible | Fully — return to original values in GUI tool |

---

## Related
- [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md) — Section 2
- [→ AUDIO-IMP-002 Dual-Mic ENC](./AUDIO-IMP-002%20—%20Dual-Mic%20ENC%20Call%20Quality.md) — Gain also applies when ENC is enabled
- [→ AUDIO-IMP-006 Adaptive ANC](./AUDIO-IMP-006%20—%20Adaptive%20ANC%20Ear-Canal%20Fit.md) — FB gain affects adaptive calibration quality
- [→ GUI TAB 04 — Microphone Config](../../SDK%20UPDATE%20FIXING/GUI%20DOCUMENTATION/TAB%2004%20—%20Microphone%20Config.md)
- [→ MAIN MIC INTEGRATION](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/MAIN%20MIC%20INTEGRATION.md)
