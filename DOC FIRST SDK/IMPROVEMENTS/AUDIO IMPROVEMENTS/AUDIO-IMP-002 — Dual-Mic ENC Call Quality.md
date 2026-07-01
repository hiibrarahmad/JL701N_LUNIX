---
tags: [audio, microphone, enc, dual-mic, call, noise-cancellation, jl7016g, improvement]
date: 2026-06-08
status: PLANNED — NOT IMPLEMENTED
effort: 🟡 Medium
risk: ⚠️ Must verify PA4 is not in GPIO conflict with ANC FF mic
priority: 10 — Medium effort, high impact
---

# 🎙️ AUDIO-IMP-002 — Dual-Mic ENC Enhanced Call Quality

> **One-line summary:** Enable 2-microphone Environmental Noise Cancellation (ENC) on the call uplink path to dramatically reduce background noise heard by the remote caller.

---

## Current State

Only **single-mic call processing** is active:

```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_AUDIO_DUAL_MIC_ENABLE    DISABLE   // 2-mic ENC off
#define TCFG_AUDIO_TRIPLE_MIC_ENABLE  DISABLE   // 3-mic off
#define TCFG_AUDIO_ADC_MIC_CHA        AUDIO_ADC_MIC_0   // only MIC0 for calls
```

Current call uplink chain:
```
MIC0 (PA1, single-ended) → CVP_DNS_MODE (DNN denoise) → mSBC/CVSD encode → phone
```

The DNN denoiser (`CVP_DNS_MODE`) is good but operates on a single channel — it cannot spatially separate voice from noise. A 2-mic setup can use beamforming to reject noise that arrives from directions other than the speaker's mouth.

---

## The Opportunity

### What Dual-Mic ENC Adds

- **Spatial beamforming:** Noise arriving from the side/back is strongly attenuated
- **Better noise floor:** Typically 10–15 dB better SNR vs single-mic in real environments
- **Works in tandem with DNN:** DNN cleans up residual noise after beamforming

### Microphone Resources Available

| Mic | Pin | Current Use | Available for ENC? |
|---|---|---|---|
| MIC0 | PA1 (ADC input) | Call mic (primary) | Already used |
| MIC1 | PA4 (MICBIAS1) | **ANC Feedforward (FF)** | ⚠️ Conflict risk |
| MIC2 | PG7 (MICBIAS2) | **ANC Feedback (FB)** | ⚠️ Conflict risk |

**Critical constraint:** MIC1 (PA4) is currently the ANC feedforward microphone. In ANC mode the hardware routes this mic to the ANC DSP, not the call ADC path. The SDK may or may not allow time-sharing between ANC and ENC — this must be verified in the SDK source before enabling.

---

## Two Possible Approaches

### Approach A — ANC-OFF during calls (Safe)
When the user is on a call, ANC is typically suspended anyway (the ANC pass-through is paused to prevent the mic from interfering with CVP). In this window, MIC1 could be redirected from the ANC path to the ENC call path.

**Config:**
```c
#define TCFG_AUDIO_DUAL_MIC_ENABLE    ENABLE
// MIC1 mode during call — SDK handles MIC rerouting during HFP connection
```

### Approach B — Dedicated 2nd call mic (Cleanest, PCB change needed)
Wire a second microphone exclusively for call ENC — does not touch the ANC mics at all. Requires a PCB revision to add a 2nd call mic channel.

---

## Recommended Config Change (Approach A — try first)

```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_AUDIO_DUAL_MIC_ENABLE    ENABLE    // was DISABLE
```

### Signal flow after change

```
MIC0 (PA1) ─┐
             ├─ 2-mic beamformer (ENC) → DNN (CVP_DNS_MODE) → mSBC → phone
MIC1 (PA4) ─┘
(ANC suspended during call — MIC1 freed for ENC)
```

---

## Risk & Trade-offs

| Aspect | Assessment |
|---|---|
| GPIO conflict during call | Low — ANC is suspended in HFP; verify in `audio_anc.c` / `earphone.c` state machine |
| ANC resumes after call | Must confirm ANC reinit after HFP disconnect (check `bt_tws.c` call state callbacks) |
| CPU overhead | DMS beamformer runs at ~64 MHz call clock — needs verification for overhead budget |
| Sound quality regression | None expected — beamformer is additive |
| Hardware requirement | None for Approach A (mics already present) |

---

## Verification Steps

1. Enable `TCFG_AUDIO_DUAL_MIC_ENABLE` and rebuild
2. Place call from phone → earphone in noisy environment (desk fan, busy room)
3. Listen on phone side: voice should be clearer, background noise attenuated
4. Check ANC resumes after hanging up: press ANC button or re-enter ANC mode
5. Monitor boot log for `dms_init` or dual-mic init messages
6. Test with ANC ON before/during/after call to confirm no state corruption

---

## Related
- [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md) — Section 2
- [→ AUDIO-IMP-009 MIC Gain Optimization](./AUDIO-IMP-009%20—%20MIC%20Gain%20Optimization.md) — Set correct gains for 2-mic mode
- [→ MAIN MIC INTEGRATION](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/MAIN%20MIC%20INTEGRATION.md)
- [→ GUI TAB 04 — Microphone Config](../../SDK%20UPDATE%20FIXING/GUI%20DOCUMENTATION/TAB%2004%20—%20Microphone%20Config.md)
- [→ GUI TAB 03 — Call Config](../../SDK%20UPDATE%20FIXING/GUI%20DOCUMENTATION/TAB%2003%20—%20Call%20Config.md)
