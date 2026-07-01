---
tags: [audio, codec, lc3, le-audio, bluetooth, jl7016g, improvement]
date: 2026-06-08
status: PLANNED — FEASIBILITY INVESTIGATION REQUIRED
effort: 🔴 High
risk: 🔴 Flash budget constraint + SDK stack support unknown
priority: 17 — Future-proofing, highest effort
---

# 🔊 AUDIO-IMP-007 — LC3 Codec / LE Audio Enable

> **One-line summary:** Enable the LC3 (Low Complexity Communication Codec) audio codec — the foundation of Bluetooth LE Audio (BT 5.2+) — to future-proof the product with dramatically better audio quality at lower bitrates than SBC, and potential for Auracast broadcast audio.

---

## Current State

LC3 decode is **disabled**:

```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_DEC_LC3_ENABLE    DISABLE
```

The current codec stack is:
- **Music decode:** SBC, AAC, LDAC
- **Call encode:** mSBC, CVSD, OPUS
- **LC3:** Not enabled

---

## What LC3 / LE Audio Offers

| Feature | SBC (current) | LC3 (proposed) |
|---|---|---|
| Bitrate at equivalent quality | 320–450 kbps | 96–192 kbps |
| Latency | 40–100 ms | 10–20 ms |
| Transparency mode audio | N/A | Excellent — low latency |
| Mono streaming | No | Yes (Auracast broadcast) |
| BT spec required | BR/EDR (Classic BT) | BLE ISO (BT 5.2+) |

LC3 uses the **isochronous (ISO) data channel** over BLE rather than the classic EDR A2DP pipe.

---

## Feasibility Constraints on This Platform

### Constraint 1 — Flash Size (1 MB)

The LC3 codec library for the JL7016G is estimated at ~80–120 KB of flash:
- Current used flash (estimate): ~700–800 KB (firmware + ANC coefficients + tone files)
- Remaining: ~200–300 KB
- LC3 library: ~80–120 KB — **borderline**
- `CONFIG_FLASH_SIZE = FLASH_SIZE_1M` — no headroom for extra features

**Option:** Upgrade PCB to 2 MB flash (see CONN-IMP-001). With 2 MB, LC3 easily fits.

### Constraint 2 — BLE ISO Channel Support

LC3 requires the **LE Isochronous Channel (CIS/BIS)** from BT 5.2. The AC701N BLE stack must support ISO — this needs verification against the JL701N SDK BLE library version:

```c
// Check in include_lib/btstack/ for:
// - ble_iso.h or ble_cis.h
// - LE audio profile headers
```

If the SDK BT stack does not include ISO support, LC3 is not feasible on this platform without a major stack upgrade from Jieli.

### Constraint 3 — Phone Side (Host)

LC3 streaming from a phone requires the phone to support **LE Audio profile (hearing access / broadcast audio)**:
- Android 13+ on Pixel 7+ and Galaxy S23+ support LC3 streaming
- iOS 17+ on iPhone 15+ includes LE Audio support
- Older phones: SBC/AAC fallback required

---

## Recommended Config Change (If Feasibility Checks Pass)

```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_DEC_LC3_ENABLE    ENABLE    // was DISABLE
```

Additional BLE audio configuration in BT stack headers (platform-specific — requires Jieli SDK documentation).

---

## Investigation Steps Before Implementing

1. **Check flash budget:** Build current firmware with `TCFG_DEC_LC3_ENABLE=ENABLE` — observe map file for size
2. **Check stack support:** Grep `include_lib/btstack/` for ISO/LE Audio headers
3. **Check Jieli SDK notes:** LC3 may require a specific SDK version or library from Jieli FAE
4. **Test phone compatibility:** Use Android phone with BT 5.2 to attempt LE Audio pairing
5. **Evaluate 2 MB flash upgrade** (see CONN-IMP-001): if flash is the blocker, upgrade hardware first

---

## Risk & Trade-offs

| Aspect | Assessment |
|---|---|
| Flash budget | Tight on 1 MB — likely requires 2 MB flash |
| SDK stack support | Unknown — must verify against BT library |
| Phone compatibility | Only BT 5.2+ phones; need SBC fallback for others |
| Dual-mode complexity | Must maintain A2DP-SBC as fallback + add LC3 path |
| Reversible | Yes — `DISABLE` reverts to current state |

---

## Related
- [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md) — Section 2
- [→ CONN-IMP-001 Double-Bank Flash](../CONNECTION%20IMPROVEMENTS/CONN-IMP-001%20—%20Simultaneous%20TWS%20OTA%20Double-Bank%20Flash.md) — 2 MB flash upgrade enables both LC3 and OTA
- [→ AUDIO CODEC QUALITY](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/AUDIO%20CODEC%20QUALITY.md)
- [→ MIGRATION COMPARISON](../../SDK%20UPDATE%20FIXING/UPDATE/MIGRATION%20COMPARISON/)
