# MAIN MIC INTEGRATION - Current SDK Path, Wiring, and Bring-up

## Scope

This document reflects the latest verified MIC fixes and the current production-intent path for JL7016G Hybrid.

It answers:
1. Where the main MIC is connected in hardware and SDK.
2. Which macros actually control MIC power and sensitivity.
3. Why the previous configuration failed and what is now correct.

---

## 1) Current Main MIC Attachment (Verified)

Active board profile:
- apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h

Main call MIC channel:
- TCFG_AUDIO_DUAL_MIC_ENABLE = DISABLE_THIS_MOUDLE
- TCFG_AUDIO_TRIPLE_MIC_ENABLE = DISABLE_THIS_MOUDLE
- TCFG_AUDIO_ADC_MIC_CHA = AUDIO_ADC_MIC_0

Physical mapping:
- AUDIO_ADC_MIC_0 -> PA1 (MIC signal input)
- PA2 -> MICBIAS power output to MIC capsule
- PA0 -> not used for MIC power on this board

---

## 2) Applied Fix Chain for Main MIC

## 2.1 FIX-012 - MIC power source corrected

Previous (broken):
- TCFG_AUDIO_MIC_PWR_CTL = MIC_PWR_FROM_MIC_LDO
- This drives MIC power on PA0, but PA0 is not connected in the schematic.

Current (fixed):
- TCFG_AUDIO_MIC_PWR_CTL = MIC_PWR_FROM_MIC_BIAS
- This enables internal MICBIAS path on PA2, which is connected in hardware.

## 2.2 FIX-013 - MIC0 mode corrected

Previous (broken):
- TCFG_AUDIO_MIC_MODE = AUDIO_MIC_CAP_DIFF_MODE
- Differential mode on a single-ended MIC0 path caused near-zero practical sensitivity.

Current (fixed):
- TCFG_AUDIO_MIC_MODE = AUDIO_MIC_CAP_MODE (single-ended for MIC0/PA1)
- TCFG_AUDIO_MIC1_MODE = AUDIO_MIC_CAP_DIFF_MODE (ANC FF)
- TCFG_AUDIO_MIC2_MODE = AUDIO_MIC_CAP_DIFF_MODE (ANC FB)

---

## 3) Runtime Path and Gain Reality

Main call capture path still runs through:
- cpu/br28/audio_enc.c
- cpu/br28/audio_capture.c
- CVP/AEC modules under apps/earphone/aec/br28/

Gain defaults are not the root issue:
- app_var.aec_mic_gain default fallback is 12 in apps/earphone/user_cfg.c
- This is already high enough to detect speech when wiring and mode are correct.

That is why the old symptom was "tap is heard but normal speech is missing": power/mode mismatch, not just gain.

---

## 4) Current Known-Good MIC Settings

From board_jl7016g_hybrid_cfg.h / board_jl7016g_hybrid.c:

| Item | Current value | Meaning |
|------|---------------|---------|
| MIC channel | AUDIO_ADC_MIC_0 | Main call MIC on PA1 |
| MIC power source | MIC_PWR_FROM_MIC_BIAS | PA2 bias power enabled |
| MIC0 mode | AUDIO_MIC_CAP_MODE | Single-ended capture |
| MIC1 mode | AUDIO_MIC_CAP_DIFF_MODE | ANC FF path |
| MIC2 mode | AUDIO_MIC_CAP_DIFF_MODE | ANC FB path |
| mic_bias_res | 4 | 2.0k ohm bias resistor |
| mic_ldo_vsel | 5 | 2.4V bias/ldo level |
| mic_dcc | 8 | DC blocking filter setting |

---

## 5) Practical Bring-up Checklist

1. Verify board macro set:
   - TCFG_AUDIO_MIC_PWR_CTL = MIC_PWR_FROM_MIC_BIAS
   - TCFG_AUDIO_MIC_MODE = AUDIO_MIC_CAP_MODE
2. Build and flash firmware.
3. Open UART logs (115200 8N1, no flow control) and confirm CVP config print.
4. Place HFP call and test at normal speaking distance.
5. Only if needed, then tune:
   - app_var.aec_mic_gain / GUI call gain
   - AGC and NS
   - NLP/AEC based on echo environment

---

## 6) Quick Diagnostics

| Symptom | Most likely cause | Check |
|--------|-------------------|-------|
| No uplink audio | MIC not powered | TCFG_AUDIO_MIC_PWR_CTL, PA2 path |
| Only tap heard, speech weak | Wrong mode (diff on single-ended MIC0) | TCFG_AUDIO_MIC_MODE |
| Speech is low but present | Gain/NS tuning | aec_mic_gain, AGC/NS settings |
| Distortion/clipping | Gain too high | aec_mic_gain and call chain gains |

---

## 7) Related Fix Notes

- FIX-012 - MIC power PA0 unconnected switched to PA2 MICBIAS
- FIX-013 - MIC0 differential mode mismatch changed to single-ended

---

## Final State

Main MIC path is now correct for this hardware: PA1 signal + PA2 bias power, with MIC0 in single-ended mode. This is the validated baseline for normal conversation pickup.

---

## Related FIX Records

| Fix | Title | Relevance |
|-----|-------|-----------|
| [FIX-012](../../FIXING/FIX-012%20—%20MIC%20power%20PA0%20unconnected%20switched%20to%20PA2%20MICBIAS.md) | MIC power PA0 → PA2 MICBIAS | Root cause: no MICBIAS power |
| [FIX-013](../../FIXING/FIX-013%20—%20MIC0%20differential%20mode%20mismatch%20changed%20to%20single-ended.md) | MIC0 differential → single-ended | Single-ended wiring mismatch |
