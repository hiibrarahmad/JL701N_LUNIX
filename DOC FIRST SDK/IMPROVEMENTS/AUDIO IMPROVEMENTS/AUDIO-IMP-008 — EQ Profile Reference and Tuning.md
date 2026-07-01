---
tags: [audio, eq, equalizer, tuning, profile, jl7016g, improvement, documentation]
date: 2026-06-08
status: DOCUMENTATION — NO CODE CHANGE REQUIRED
effort: 🟢 Low
risk: ✅ Safe — configuration only, fully reversible via GUI
priority: 8 — Doc + tuning guide, immediate usability value
---

# 🔊 AUDIO-IMP-008 — EQ Profile Reference and Tuning

> **One-line summary:** The SDK already has a 10-band EQ enabled — this document provides reference frequency profiles for common use cases (flat reference, bass boost, vocal clarity, ANC transparency) and explains the full AC701N GUI tuning workflow.

---

## Current State

EQ is **enabled** with offline coefficients:

```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_EQ_ENABLE             1   // 10-band EQ
#define TCFG_BT_MUSIC_EQ_ENABLE    1   // BT music EQ
#define TCFG_PHONE_EQ_ENABLE       1   // Call path EQ (DL: 3-band, UL: 3-band)
```

No documented reference profiles exist in the vault — the current coefficients are whatever was last written to flash via the AC701N Config GUI tool. Without a reference profile document it is impossible to reproduce or iterate on the sound signature.

---

## EQ Architecture on JL7016G

```
BT A2DP stream
    │
    ▼
SBC / AAC / LDAC decode (stereo → mono-L)
    │
    ▼
10-band parametric EQ
│  Band 1:   60 Hz   ← sub-bass
│  Band 2:  125 Hz   ← bass
│  Band 3:  250 Hz   ← low-mid
│  Band 4:  500 Hz   ← mid
│  Band 5: 1000 Hz   ← upper-mid (1 kHz reference)
│  Band 6: 2000 Hz   ← presence
│  Band 7: 4000 Hz   ← upper presence
│  Band 8: 6000 Hz   ← air / sibilance
│  Band 9: 8000 Hz   ← treble
│ Band 10:12000 Hz   ← high treble
    │
    ▼
DRC (when AUDIO-IMP-001 enabled)
    │
    ▼
Digital volume (–6 dB cap with ANC)
    │
    ▼
DAC → speaker
```

Each band supports: **Gain** (± 12 dB), **Frequency** (adjustable), **Q factor** (0.5–10).

---

## Reference EQ Profiles

### Profile 1 — Flat Reference (Testing Baseline)

All bands at 0 dB. Use this as a starting point for measurement.

| Band | Freq | Gain | Q |
|---|---|---|---|
| 1 | 60 Hz | 0 dB | 0.7 |
| 2 | 125 Hz | 0 dB | 0.7 |
| 3 | 250 Hz | 0 dB | 0.7 |
| 4 | 500 Hz | 0 dB | 0.7 |
| 5 | 1 kHz | 0 dB | 0.7 |
| 6 | 2 kHz | 0 dB | 0.7 |
| 7 | 4 kHz | 0 dB | 0.7 |
| 8 | 6 kHz | 0 dB | 0.7 |
| 9 | 8 kHz | 0 dB | 0.7 |
| 10 | 12 kHz | 0 dB | 0.7 |

---

### Profile 2 — Consumer V-Curve (Bass + Treble Boost)

Suits pop, hip-hop, EDM. Warm bass, sparkly treble, slight mid recession.

| Band | Freq | Gain | Q |
|---|---|---|---|
| 1 | 60 Hz | +4 dB | 0.7 |
| 2 | 125 Hz | +3 dB | 0.8 |
| 3 | 250 Hz | +1 dB | 1.0 |
| 4 | 500 Hz | -1 dB | 1.0 |
| 5 | 1 kHz | -2 dB | 1.0 |
| 6 | 2 kHz | -1 dB | 1.0 |
| 7 | 4 kHz | +1 dB | 1.0 |
| 8 | 6 kHz | +2 dB | 1.2 |
| 9 | 8 kHz | +3 dB | 0.8 |
| 10 | 12 kHz | +2 dB | 0.7 |

---

### Profile 3 — Vocal Clarity (Podcast / Call Monitor)

Boosts speech intelligibility. Suits podcasts, voice calls monitoring.

| Band | Freq | Gain | Q |
|---|---|---|---|
| 1 | 60 Hz | -3 dB | 0.7 |
| 2 | 125 Hz | -2 dB | 0.7 |
| 3 | 250 Hz | 0 dB | 0.7 |
| 4 | 500 Hz | +1 dB | 1.2 |
| 5 | 1 kHz | +3 dB | 1.2 |
| 6 | 2 kHz | +4 dB | 1.5 |
| 7 | 4 kHz | +2 dB | 1.2 |
| 8 | 6 kHz | 0 dB | 0.7 |
| 9 | 8 kHz | -1 dB | 0.7 |
| 10 | 12 kHz | -2 dB | 0.7 |

---

### Profile 4 — ANC Compensation (for ANC mode only)

ANC creates a low-frequency resonance artifact around 200–400 Hz and sometimes a dip around 2–4 kHz. This profile compensates:

| Band | Freq | Gain | Q |
|---|---|---|---|
| 1 | 60 Hz | 0 dB | 0.7 |
| 2 | 125 Hz | -1 dB | 1.0 |
| 3 | 250 Hz | -2 dB | 1.2 |
| 4 | 500 Hz | -1 dB | 1.0 |
| 5 | 1 kHz | 0 dB | 0.7 |
| 6 | 2 kHz | +2 dB | 1.5 |
| 7 | 4 kHz | +3 dB | 1.2 |
| 8 | 6 kHz | +1 dB | 0.8 |
| 9 | 8 kHz | 0 dB | 0.7 |
| 10 | 12 kHz | 0 dB | 0.7 |

---

## How to Apply a Profile — GUI Workflow

1. Open **AC701N Config GUI Tool** (offline mode)
2. Select **TAB 06 — Volume Config** (for music EQ gains)
3. Enter 10-band values from table above
4. Click **Generate** → offline `.bin` file created
5. Program the bin file to flash via ISD download tool
6. Verify in UART log: look for `eq_init` and `eq coeff loaded`

For call path EQ (3-band DL / 3-band UL): use **TAB 03 — Call Config**.

---

## ANC Tool Online Mode (For Live EQ Tuning)

If `TCFG_ANC_TOOL_DEBUG_ONLINE=ENABLE` is temporarily turned on:
- Connect the ANC tuning tool via BLE/SPP
- Adjust EQ bands live while music plays
- Export the final profile to offline file for production flash

**Note:** `TCFG_ANC_TOOL_DEBUG_ONLINE` should be `DISABLE` in production builds — it exposes internal state over BLE.

---

## Related
- [→ GUI TAB 06 — Volume Config](../../SDK%20UPDATE%20FIXING/GUI%20DOCUMENTATION/TAB%2006%20—%20Volume%20Config.md)
- [→ GUI TAB 03 — Call Config](../../SDK%20UPDATE%20FIXING/GUI%20DOCUMENTATION/TAB%2003%20—%20Call%20Config.md)
- [→ AUDIO-IMP-001 DRC](./AUDIO-IMP-001%20—%20DRC%20Dynamic%20Range%20Compression.md) — Enable DRC after EQ tuning
- [→ AUDIO CODEC QUALITY](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/AUDIO%20CODEC%20QUALITY.md)
