---
tags: [connection, bluetooth, clock, frequency, power, performance, jl7016g, improvement]
date: 2026-06-08
status: ANALYSIS — TUNING RECOMMENDED AFTER MEASUREMENT
effort: 🟡 Medium
risk: ⚠️ Incorrect clock for a state = glitches or packet loss — must test each mode
priority: 14 — Medium effort, moderate power savings possible
---

# 📡 CONN-IMP-007 — BT Clock Frequency Optimization

> **One-line summary:** The CPU clock steps up at each BT activity level. Some clock values may be higher than needed (wasting power) or too low (causing audio dropout). This document analyzes each clock setting and provides recommended tuning targets.

---

## Current Clock Table

From `board_jl7016g_hybrid_cfg.h`:

```c
#define CONFIG_BT_NORMAL_HZ        24000000    //  24 MHz — BT idle (connected, no audio)
#define CONFIG_BT_CONNECT_HZ       48000000    //  48 MHz — BT connected transition
#define CONFIG_BT_A2DP_HZ          96000000    //  96 MHz — A2DP music streaming with EQ
#define CONFIG_BT_CALL_HZ          64000000    //  64 MHz — HFP call (CVSD/mSBC)
#define CONFIG_BT_CALL_16k_HZ      80000000    //  80 MHz — HFP 16kHz wide-band call
#define CONFIG_BT_CALL_DNS_HZ      96000000    //  96 MHz — call with DNN denoise active
```

---

## Analysis Per Clock State

### State 1 — `CONFIG_BT_NORMAL_HZ = 24 MHz` (BT Idle)

**Purpose:** CPU clock when BT is connected but no audio is streaming.
**Current value:** 24 MHz
**Assessment:** ✅ Correct — minimum viable clock for BT connection maintenance + TWS heartbeat. No known issue.
**Recommendation:** Keep at 24 MHz. Reducing further would require deep sleep (see CONN-IMP-004).

---

### State 2 — `CONFIG_BT_CONNECT_HZ = 48 MHz` (Connection Transition)

**Purpose:** Clock during BT scan, pairing, and profile negotiation.
**Current value:** 48 MHz
**Assessment:** ✅ Likely adequate. SDP service browsing and profile negotiation are not compute-heavy.
**Recommendation:** Try 32 MHz — if pairing completes successfully (SDP browsing < 3s), drop to 32 MHz and save ~15 mA during the 2–5s connection window.

```c
#define CONFIG_BT_CONNECT_HZ    32000000   // try 32 MHz (was 48 MHz)
```

---

### State 3 — `CONFIG_BT_A2DP_HZ = 96 MHz` (Music Streaming)

**Purpose:** CPU clock during A2DP music streaming **with 10-band EQ active**.
**Current value:** 96 MHz
**Assessment:** ⚠️ Needed for EQ + LDAC. LDAC at 990 kbps + EQ processing requires ~80–96 MHz. For SBC or AAC (lower bitrate), this may be reducible.

**Optimization:**
- SBC/AAC without LDAC: try 80 MHz
- LDAC at 660 kbps: try 80 MHz
- LDAC at 990 kbps with EQ: keep 96 MHz

```c
// If LDAC is primary codec (with EQ): keep 96 MHz
// If mostly SBC/AAC: lower to 80 MHz and test for audio dropouts
#define CONFIG_BT_A2DP_HZ    80000000   // try (was 96 MHz) — test for LDAC dropout
```

**Test:** Play LDAC at max quality setting, verify no audio glitches or buffer underrun messages in UART log.

---

### State 4 — `CONFIG_BT_CALL_HZ = 64 MHz` (HFP Call, CVSD/mSBC)

**Purpose:** Clock during HFP voice calls with standard or wide-band codec.
**Current value:** 64 MHz
**Assessment:** ✅ Well-sized for mSBC encode + CVP (without DNN). mSBC compression is not DSP-heavy.
**Optimization potential:** Try 48 MHz for CVSD calls (narrow-band, 8 kHz sampling — much lighter).

```c
// CVSD only calls (narrow-band, 8 kHz):
#define CONFIG_BT_CALL_HZ    48000000   // try (was 64 MHz) — test call quality
// Wide-band mSBC: keep at 64 MHz
```

---

### State 5 — `CONFIG_BT_CALL_16k_HZ = 80 MHz` (16 kHz Wide-Band Call)

**Purpose:** mSBC wide-band call at 16 kHz sample rate.
**Current value:** 80 MHz
**Assessment:** ✅ Appropriate. 16 kHz sample rate doubles the filter workload vs 8 kHz.
**Recommendation:** Keep at 80 MHz. 64 MHz may cause occasional dropout — not worth the small saving.

---

### State 6 — `CONFIG_BT_CALL_DNS_HZ = 96 MHz` (Call + DNN Denoise)

**Purpose:** Call clock when DNN (Deep Neural Network) denoiser is active.
**Current value:** 96 MHz
**Assessment:** ✅ Required — the DNN inference is the most compute-intensive operation in the SDK. Running at < 96 MHz causes DNN frame processing overrun and audible artifacts.
**Recommendation:** Do NOT reduce. Keep at 96 MHz.

---

## Power Savings Summary

| State | Current | Recommended | Estimated Saving |
|---|---|---|---|
| NORMAL idle | 24 MHz | 24 MHz | None (already min) |
| CONNECT transition | 48 MHz | 32 MHz (test) | ~12 mW for ~3–5s per connect |
| A2DP SBC/AAC | 96 MHz | 80 MHz (test) | ~15 mW continuous |
| A2DP LDAC max | 96 MHz | 96 MHz (keep) | None needed |
| CALL CVSD | 64 MHz | 48 MHz (test) | ~8 mW during calls |
| CALL mSBC 16k | 80 MHz | 80 MHz (keep) | None needed |
| CALL + DNN | 96 MHz | 96 MHz (keep) | None — required |

*Power estimates: ~1 mW per MHz at 3.7V supply, LDO efficiency 70%*

---

## How to Measure If Clock Is Sufficient

Monitor UART log for these patterns during each state:

| Log Pattern | Meaning | Action |
|---|---|---|
| `a2dp underrun` or `buf_empty` | A2DP buffer ran dry — clock too low | Raise clock |
| `sbc decode timeout` | SBC frame missed — clock too low | Raise clock |
| `dns frame overrun` | DNN couldn't complete in time | Raise clock (or keep at 96 MHz) |
| No errors after 10 min continuous | Clock is sufficient | Consider lowering by 8 MHz and test again |

---

## Risk & Trade-offs

| Aspect | Assessment |
|---|---|
| Audio dropout if clock too low | Audible glitches — immediately obvious in testing |
| Saving from correct tuning | 10–20 mW in A2DP = meaningful battery improvement |
| Test coverage needed | Each mode (SBC, AAC, LDAC, CVSD, mSBC, DNN) must be tested independently |
| Reversible | Yes — revert constants and rebuild |

---

## Recommended Testing Order

1. Lower `CONFIG_BT_CONNECT_HZ` to 32 MHz → test 10× connections → no issue? ✅
2. Lower `CONFIG_BT_A2DP_HZ` to 80 MHz → test SBC, AAC, LDAC streams → no dropout? ✅
3. Lower `CONFIG_BT_CALL_HZ` to 48 MHz → test CVSD call quality → clear audio? ✅
4. Document final verified values in this document

---

## Related
- [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md) — Section 5
- [→ CONN-IMP-004 Low Power Mode](./CONN-IMP-004%20—%20Low%20Power%20Mode%20Enable.md) — Low power and clock optimization are complementary
- [→ POWER DEEP DIVE](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/POWER%20DEEP%20DIVE.md)
- [→ AUDIO CODEC QUALITY](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/AUDIO%20CODEC%20QUALITY.md) — Clock requirements per codec
