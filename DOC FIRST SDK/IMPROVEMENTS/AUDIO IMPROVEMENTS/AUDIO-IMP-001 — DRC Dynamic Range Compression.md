---
tags: [audio, drc, compression, loudness, jl7016g, improvement]
date: 2026-06-08
status: PLANNED — NOT IMPLEMENTED
effort: 🟢 Low
risk: ✅ Safe — pure software, no hardware dependency
priority: ⭐ 1 — Highest priority low-effort item
---

# 🔊 AUDIO-IMP-001 — DRC Dynamic Range Compression

> **One-line summary:** Enable DRC on both the music and call paths to prevent clipping, smooth loudness jumps, and protect the speaker at high volume — currently fully disabled.

---

## Current State

DRC is **disabled** on all audio paths:

```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_DRC_ENABLE              0   // music path
#define TCFG_BT_MUSIC_DRC_ENABLE     0   // BT music path
// hearing aid DRC would enable this, but HEARING_AID_ENABLE is also off
```

The volume chain currently is:
```
BT A2DP → SBC/AAC/LDAC decode → 10-band EQ → Digital volume (capped -6 dB) → DAC
```
With no DRC, a loud passage encoded at 0 dBFS will hit the DAC at maximum level with no protection. Because `DIG_VOL_MAX_VALUE = -6.0 dB` the headroom is just 6 dB — not enough to catch transient peaks safely.

---

## The Problem

| Symptom | Cause |
|---|---|
| Clipping on loud content at mid-high volume | No limiter stage after EQ |
| Volume jumps feel harsh between quiet/loud tracks | No automatic gain control |
| Perceived loudness varies heavily by source material | No normalization stage |
| Speaker driver may be stressed by transient peaks | No peak limiter |

---

## Recommended Change

Enable DRC for the BT music path. The call path DRC is lower priority since CVP/DNS already provides gain riding.

### Config change (1 line each)

```c
// board_jl7016g_hybrid_cfg.h — change both to 1
#define TCFG_DRC_ENABLE              1   // was 0
#define TCFG_BT_MUSIC_DRC_ENABLE     1   // was 0
```

### What the SDK DRC provides

The JL7016G DRC is a multi-band compressor/limiter implemented in the DSP. When enabled:
- **Attack time:** ~5 ms (catches transient peaks quickly)
- **Release time:** ~100 ms (smooth release, no pumping)
- **Ratio:** Configurable via AC701N Config GUI → **TAB 06 — Volume Config**
- **Threshold:** Set via GUI or offline coefficient file
- **Look-ahead limiter:** Built in — prevents any sample exceeding threshold reaching DAC

### Audio signal flow after change

```
BT A2DP → decode → 10-band EQ → DRC (compress/limit) → Digital vol (-6 dB cap) → DAC
```

---

## Risk & Trade-offs

| Aspect | Assessment |
|---|---|
| Sound character change | Yes — loud passages will be quieter; some users prefer uncompressed |
| CPU overhead | ~2–5 MHz at 96 MHz A2DP clock — negligible |
| Flash cost | None — DRC library already linked when EQ is enabled |
| Hearing aid conflict | None — `HEARING_AID_ENABLE` is OFF; no interaction |
| Reversible | Yes — set back to 0 to disable |

---

## Verification Steps

1. Enable flags and build firmware
2. Flash to left bud (test bud)
3. Play a track with large dynamic range (e.g., classical with loud crescendo or pop with heavy bass drop)
4. Increase volume to max (level 16)
5. Confirm: no audible clipping/distortion
6. Compare perceived loudness consistency across 3 different tracks
7. Check boot log: DRC module should report init at startup (search for `drc_init` or `drc open`)

---

## Related
- [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md) — Section 2 (disabled flags)
- [→ AUDIO-IMP-010 Volume Ceiling](./AUDIO-IMP-010%20—%20Volume%20Ceiling%20and%20ANC%20Cap%20Analysis.md) — DRC works best after ceiling review
- [→ GUI TAB 06 — Volume Config](../../SDK%20UPDATE%20FIXING/GUI%20DOCUMENTATION/TAB%2006%20—%20Volume%20Config.md)
- [→ AUDIO DEEP DIVE](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/AUDIO%20DEEP%20DIVE.md)
