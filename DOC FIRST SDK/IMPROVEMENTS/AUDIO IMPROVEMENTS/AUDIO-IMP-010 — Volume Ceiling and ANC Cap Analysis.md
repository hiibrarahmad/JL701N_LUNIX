---
tags: [audio, volume, anc, ceiling, dac, loudness, jl7016g, improvement]
date: 2026-06-08
status: PLANNED — TEST REQUIRED BEFORE CHANGE
effort: 🟢 Low
risk: ⚠️ Test for distortion before raising — DAC can clip without DRC protection
priority: 7 — Low effort, verify DRC (AUDIO-IMP-001) is on before applying
---

# 🔊 AUDIO-IMP-010 — Volume Ceiling and ANC Cap Analysis

> **One-line summary:** The maximum digital volume is capped at −6 dB specifically because ANC is enabled. This analysis determines whether the cap can be safely raised (or removed) once DRC is enabled, and documents the exact relationship between the ANC volume cap and the DAC headroom.

---

## Current State

The volume ceiling is enforced in `audio_config.h`:

```c
// cpu/br28/audio_config.h
// JL7016G Hybrid + ANC: volume cap at -6 dBFS
#define DIG_VOL_MAX_VALUE    -6.0    // dBFS — reduced from 0 dB due to ANC
#define DIG_VOL_STEP         -3.0    // dB per step down from max
#define SYS_MAX_VOL          MAX_DIG_VOL   // 16 levels total
```

Volume level mapping (with current cap):
| Level | Gain (dBFS) |
|---|---|
| 16 (max) | **−6 dB** |
| 15 | −9 dB |
| 14 | −12 dB |
| ... | ... |
| 1 | −51 dB |
| 0 | Mute |

At level 16 the user gets −6 dBFS — 6 dB below full scale. This is intentional safety margin.

---

## Why the Cap Exists — ANC Interaction

When ANC is active the ANC DSP injects an anti-noise signal into the DAC path. This anti-noise is added to the audio signal **after** the digital volume stage:

```
Digital audio (vol = -6 dB) ──┐
                               ├─→ DAC
ANC anti-noise signal  ────────┘
```

If the audio is at 0 dBFS (no cap) and the ANC anti-noise is at −6 dBFS (typical), the combined signal can reach +0 to +6 dBFS → **DAC clipping**.

The −6 dB cap ensures that even when ANC anti-noise is at its maximum contribution, the combined signal stays at or below 0 dBFS.

---

## The Opportunity

With **DRC enabled** (AUDIO-IMP-001):
- The DRC limiter stage sits **before** the volume stage
- It prevents the audio source material from exceeding a configurable threshold (e.g., −3 dBFS)
- The ANC anti-noise is still added after volume, but the source material is already limited

This creates headroom to raise the volume cap from −6 dB toward −3 dB (or even 0 dB with a limiter tuned correctly).

```
Source → DRC (limit at -3 dBFS) → vol (at -3 dB cap) → sum with ANC (-6 dBFS) → DAC
Max combined: -3 + (-3) + (-6) dBFS = worst case = 0 dBFS  ← no clipping
```

---

## Recommended Change (After DRC is Enabled)

### Step 1 — Enable DRC first
See [AUDIO-IMP-001](./AUDIO-IMP-001%20—%20DRC%20Dynamic%20Range%20Compression.md). Do not raise volume ceiling without limiter protection.

### Step 2 — Raise ceiling incrementally

```c
// cpu/br28/audio_config.h
#define DIG_VOL_MAX_VALUE    -3.0    // was -6.0 — raise by 3 dB (test first)
```

Test at −3 dB. If no distortion is heard at max volume on loud content → consider raising to −1.5 dB or 0 dB.

### Step 3 — Measure DAC output

Use UART logging or an audio analyzer to confirm DAC output does not exceed 0 dBFS when:
- ANC is ON at typical noise environment
- Audio stream is loud test tone (0 dBFS 1 kHz)
- Volume at maximum

---

## Without DRC — What NOT to Do

Raising `DIG_VOL_MAX_VALUE` above −6 dB **without DRC** risks:
- Speaker driver overstress during transient peaks (e.g., kick drum)
- DAC output clipping — audible as harsh distortion
- Potential long-term speaker cone damage at sustained maximum level

The −6 dB cap without DRC is the correct and safe default.

---

## Volume Step Tuning (Separate Consideration)

The current step is −3 dB (coarse). Each volume increment feels like a large jump. Consider:

```c
#define DIG_VOL_STEP    -2.0    // smoother steps (was -3.0)
// Note: with SYS_MAX_VOL = 16 and step -2.0, range = 0 to -30 dB
// vs current: 0 to -45 dB with step -3.0
```

Finer steps sacrifice maximum range — decide based on user preference.

---

## Risk & Trade-offs

| Aspect | Assessment |
|---|---|
| DAC clipping without DRC | High risk — do not raise ceiling without AUDIO-IMP-001 |
| Speaker damage | Possible if threshold exceeded repeatedly |
| Perceived loudness gain | 3 dB increase is audible — users will notice |
| Reversible | Yes — change `DIG_VOL_MAX_VALUE` back |
| ANC quality affected | No — ANC coefficients are independent of volume cap |

---

## Verification Steps

1. Enable DRC (AUDIO-IMP-001 first)
2. Change `DIG_VOL_MAX_VALUE` to −3.0 dB
3. Play 0 dBFS 1 kHz test tone at maximum volume with ANC ON
4. Monitor UART: look for any clipping flags or DRC trigger counts
5. Listen: confirm no audible distortion, harshness, or speaker stress
6. Reduce to −1.5 dB and repeat if −3 dB passes
7. Document final safe ceiling in this document

---

## Related
- [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md) — Section 2
- [→ AUDIO-IMP-001 DRC](./AUDIO-IMP-001%20—%20DRC%20Dynamic%20Range%20Compression.md) — **Required before raising ceiling**
- [→ AUDIO-IMP-008 EQ Profile](./AUDIO-IMP-008%20—%20EQ%20Profile%20Reference%20and%20Tuning.md) — EQ shapes affect peak levels
- [→ GUI TAB 06 — Volume Config](../../SDK%20UPDATE%20FIXING/GUI%20DOCUMENTATION/TAB%2006%20—%20Volume%20Config.md)
