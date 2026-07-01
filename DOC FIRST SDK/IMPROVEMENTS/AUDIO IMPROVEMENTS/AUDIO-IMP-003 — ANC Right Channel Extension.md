---
tags: [audio, anc, right-channel, hardware, microphone, jl7016g, improvement]
date: 2026-06-08
status: PLANNED — HARDWARE REQUIRED FIRST
effort: 🔴 High
risk: 🔴 Requires PCB revision — right-bud microphone wiring
priority: 15 — High effort, high impact
---

# 🔊 AUDIO-IMP-003 — ANC Right Channel Extension

> **One-line summary:** Extend ANC to the right earbud. Currently ANC operates on the left channel only — the right earbud passes audio without any noise cancellation. True stereo ANC requires dedicated feedforward and feedback microphones wired to the right-bud AC701N.

---

## Current State

ANC is **left channel only**:

```c
// board_jl7016g_hybrid_cfg.h
#define ANC_CH          ANC_L_CH      // left channel ANC
#define ANCL_FF_MIC     A_MIC1        // MIC1 = feedforward mic
#define ANCL_FB_MIC     A_MIC2        // MIC2 = feedback/error mic

#define ANCR_FF_MIC     MIC_NULL      // RIGHT feedforward = NONE
#define ANCR_FB_MIC     MIC_NULL      // RIGHT feedback   = NONE
```

The right bud receives the same ANC-processed audio from the left bud via TWS sync, but no actual active noise cancellation is running on the right side. The effect: the right ear hears more environmental noise than the left.

---

## Why This Matters

In a real TWS product with hybrid ANC:
- **Left bud:** FF mic captures outside noise → ANC DSP generates anti-noise → FB mic measures residual → corrects → clean audio delivered to ear
- **Right bud (current):** No FF/FB mic processing. The right DAC receives the left bud's audio mix but the right ear canal does not have a dedicated anti-noise signal tuned to its own acoustic environment

For casual use this is acceptable. For a premium noise-cancellation product it is a significant asymmetry.

---

## What Is Required

### Hardware (PCB Change Required)

The right earbud AC701N has the same ANC-capable ADC inputs as the left. The physical microphones must be wired on the right-bud PCB:

| Mic Role | Pin on Right AC701N | Required Component |
|---|---|---|
| ANCR_FF_MIC (feedforward) | PA4 (same as left MIC1) | MEMS microphone (e.g., ZTS6216 or equivalent) on right PCB outside shell |
| ANCR_FB_MIC (feedback/error) | PG7 (same as left MIC2) | MEMS microphone on right PCB inside ear canal |
| MICBIAS power | PA4 internal LDO | Already present on AC701N — no extra component |

### Firmware (After PCB Has Mics)

```c
// board_jl7016g_hybrid_cfg.h — change after hardware is ready
#define ANC_CH          ANC_LR_CH     // both channels  (was ANC_L_CH)
#define ANCR_FF_MIC     A_MIC1        // right FF = MIC1 on right bud
#define ANCR_FB_MIC     A_MIC2        // right FB = MIC2 on right bud
```

### ANC Coefficient Calibration

Extending to the right channel requires a **separate ANC filter calibration** for the right ear cup geometry:
1. Use the ANC tuning tool (enable `TCFG_ANC_TOOL_DEBUG_ONLINE=ENABLE` temporarily)
2. Run the ISD/earphone-side calibration with the right bud in-ear
3. Save right-channel ANCIF coefficients to flash at `ANCIF1_ADR: 0xFD100` (currently only left-channel data)

---

## Architecture After Change

```
Left Bud (current):
  MIC1(PA4) FF → ANC DSP → anti-noise L → DAC L
  MIC2(PG7) FB ───────────────────┘

Right Bud (after improvement):
  MIC1(PA4) FF → ANC DSP → anti-noise R → DAC R
  MIC2(PG7) FB ───────────────────┘

TWS Link: audio sync only — each bud runs independent ANC loop
```

---

## Risk & Trade-offs

| Aspect | Assessment |
|---|---|
| PCB redesign scope | Both right-bud shell: 2 additional mics + traces |
| Calibration effort | Full right-channel ANC tuning session required |
| BOM cost increase | +2 MEMS mics per pair |
| Firmware risk | Moderate — SDK supports dual-channel ANC, tested on Jieli reference designs |
| TWS sync interaction | ANC runs independently per bud — no sync conflict |
| Reversible | Yes — revert `ANC_CH` to `ANC_L_CH` |

---

## Recommended Sequence

1. ✅ Confirm left-bud ANC is working well (FIX-020 through FIX-022 completed)
2. 🔧 Commission PCB revision for right-bud mic wiring
3. 🔧 Enable `ANC_CH = ANC_LR_CH` and right-mic flags
4. 🔧 Run ANC calibration on right channel
5. 🧪 Listen test: noise reduction symmetry in both ears

---

## Related
- [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md) — Section 2
- [→ GUI TAB 07 — ANC Config](../../SDK%20UPDATE%20FIXING/GUI%20DOCUMENTATION/TAB%2007%20—%20ANC%20Config.md)
- [→ AUDIO-IMP-004 Wind Noise](./AUDIO-IMP-004%20—%20Wind%20Noise%20Detection.md) — Enable alongside right-channel ANC
- [→ AUDIO-IMP-006 Adaptive ANC](./AUDIO-IMP-006%20—%20Adaptive%20ANC%20Ear-Canal%20Fit.md) — Calibration step is shared
