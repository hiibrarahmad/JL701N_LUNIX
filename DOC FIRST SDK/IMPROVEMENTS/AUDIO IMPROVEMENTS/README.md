---
tags: [audio, improvements, index, eq, anc, drc, enc, codec, jl7016g]
date: 2026-06-08
status: IN PROGRESS — ACTIVE PLANNING
---

# 🔊 Audio Improvements — Index

> 10 audio improvement opportunities identified from the JL7016G Hybrid SDK audit.
> Ordered by effort: start with 🟢 Low items for immediate gains.
> [→ Back to IMPROVEMENTS/README.md](../README.md) | [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md)

---

## All Audio Improvements

| ID | Title | Effort | Risk | Status |
|---|---|---|---|---|
| [AUDIO-IMP-001](./AUDIO-IMP-001%20—%20DRC%20Dynamic%20Range%20Compression.md) | DRC — Dynamic Range Compression | 🟢 Low | ✅ Safe | ⏳ Pending |
| [AUDIO-IMP-002](./AUDIO-IMP-002%20—%20Dual-Mic%20ENC%20Call%20Quality.md) | Dual-Mic ENC — Enhanced Call Quality | 🟡 Medium | ⚠️ Verify PA4 | ⏳ Pending |
| [AUDIO-IMP-003](./AUDIO-IMP-003%20—%20ANC%20Right%20Channel%20Extension.md) | ANC Right Channel Extension | 🔴 High | 🔴 Hardware | ⏳ Pending |
| [AUDIO-IMP-004](./AUDIO-IMP-004%20—%20Wind%20Noise%20Detection.md) | Wind Noise Detection | 🟢 Low | ✅ Safe | ⏳ Pending |
| [AUDIO-IMP-005](./AUDIO-IMP-005%20—%20Speak-to-Chat%20Transparency%20Mode.md) | Speak-to-Chat Transparency Mode | 🟢 Low | ✅ Safe | ⏳ Pending |
| [AUDIO-IMP-006](./AUDIO-IMP-006%20—%20Adaptive%20ANC%20Ear-Canal%20Fit.md) | Adaptive ANC — Ear-Canal Personalization | 🟡 Medium | ⚠️ Calibration | ⏳ Pending |
| [AUDIO-IMP-007](./AUDIO-IMP-007%20—%20LC3%20Codec%20LE%20Audio.md) | LC3 Codec / LE Audio Enable | 🔴 High | 🔴 Flash + stack | ⏳ Pending |
| [AUDIO-IMP-008](./AUDIO-IMP-008%20—%20EQ%20Profile%20Reference%20and%20Tuning.md) | EQ Profile Reference and Tuning | 🟢 Low | ✅ Safe | ⏳ Pending |
| [AUDIO-IMP-009](./AUDIO-IMP-009%20—%20MIC%20Gain%20Optimization.md) | MIC Gain Optimization | 🟢 Low | ✅ Safe | ⏳ Pending |
| [AUDIO-IMP-010](./AUDIO-IMP-010%20—%20Volume%20Ceiling%20and%20ANC%20Cap%20Analysis.md) | Volume Ceiling and ANC Cap Analysis | 🟢 Low | ⚠️ Test loudness | ⏳ Pending |

---

## Quick Context — Current Audio State

```
DAC:   Mono-L, Differential, ANC capped at -6 dB max, 16 vol steps
ADC:   MIC0 (PA1) single-ended call mic, MIC1 (PA4) FF, MIC2 (PG7) FB
ANC:   Hybrid FF+FB, left channel ONLY (right = MIC_NULL)
EQ:    10-band music, 3-band call DL/UL — offline coefficients
DRC:   DISABLED for music AND call paths
Codec: SBC + AAC + LDAC decode | mSBC + CVSD + OPUS encode
Denoise: DNN (CVP_DNS_MODE) — 96 MHz clock when active
```

---

## Related
- [→ AUDIO DEEP DIVE](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/AUDIO%20DEEP%20DIVE.md)
- [→ AUDIO CODEC QUALITY](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/AUDIO%20CODEC%20QUALITY.md)
- [→ MAIN MIC INTEGRATION](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/MAIN%20MIC%20INTEGRATION.md)
- [→ ARCHITECTURE/02-AUDIO-SYSTEM.md](../../SDK%20UPDATE%20FIXING/ARCHITECTURE/02-AUDIO-SYSTEM.md)
