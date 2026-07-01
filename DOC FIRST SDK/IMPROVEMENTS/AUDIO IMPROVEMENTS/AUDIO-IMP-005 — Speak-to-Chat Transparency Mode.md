---
tags: [audio, anc, speak-to-chat, transparency, passthrough, jl7016g, improvement]
date: 2026-06-08
status: PLANNED — NOT IMPLEMENTED
effort: 🟢 Low
risk: ✅ Safe — software flag only
priority: ⭐ 3 — High UX value, zero hardware cost
---

# 🔊 AUDIO-IMP-005 — Speak-to-Chat Transparency Mode

> **One-line summary:** Enable automatic ANC pause when the user speaks — the SDK's Speak-to-Chat feature detects the user's voice via the FB mic and transitions into transparency (passthrough) mode so they can hear their surroundings and speak naturally without removing the earbuds.

---

## Current State

Speak-to-Chat is **disabled**:

```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_AUDIO_SPEAK_TO_CHAT_ENABLE    DISABLE
```

When ANC is ON, the user is isolated from their environment. To talk to someone nearby they must either:
- Remove one earbud
- Manually press the ANC button to toggle to transparency/off
- Speak louder than normal while muffled

This is a significant UX pain point that flagship ANC earphones (AirPods Pro, Sony WF-1000XM5, Bose QC Earbuds) all solve with automatic speak-to-chat.

---

## How It Works in This SDK

The speak-to-chat detector uses the **feedback/error microphone** (ANCL_FB_MIC = A_MIC2 on PG7) which faces the ear canal. When the user starts speaking, their voice is conducted through bone/tissue and picked up by the FB mic even with ANC active.

```
FB Mic (PG7, in-ear) → voice activity detector (VAD)
                              │
                    Voice detected?
                         │
                  YES ───▼
                     Pause ANC → open transparency passthrough
                     Music/call attenuated (SDK-configurable)
                  NO  → resume ANC after timeout
```

### Transparency mode in this SDK

The SDK's transparency path routes the feedforward mic (external sound) to the DAC output mixed with the audio stream — the user hears both their music and the outside world simultaneously. When speak-to-chat triggers, this mode activates automatically.

---

## Recommended Change

```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_AUDIO_SPEAK_TO_CHAT_ENABLE    ENABLE    // was DISABLE
```

### Optional companion flag (also disabled)

```c
// Optionally enable wide-area tap detection alongside speak-to-chat
// for double-tap to toggle transparency manually
#define TCFG_AUDIO_WIDE_AREA_TAP_ENABLE    ENABLE    // currently DISABLE
```

### Recommended GUI tuning (TAB 07 — ANC Config)

| Parameter | Suggested Start | Notes |
|---|---|---|
| VAD trigger threshold | Medium-high | Avoid false trigger from ambient speech |
| Speak-to-chat hold time | 3–5 seconds | How long transparency stays on after speech stops |
| Music attenuation | -12 dB | Quiet music so user can hear themselves |
| Re-ANC transition | Smooth (500 ms) | Avoid click when ANC re-engages |

---

## Risk & Trade-offs

| Aspect | Assessment |
|---|---|
| False triggers | Possible in loud environments where ambient speech triggers VAD — tune threshold |
| Battery impact | < 2% — VAD runs in ANC context already active |
| Audio interruption | Music dips briefly when speak-to-chat activates — expected, configurable |
| Works without ANC? | No — speak-to-chat only fires when ANC mode is active |
| Reversible | Yes — set `DISABLE` to revert |

---

## UX Flow After Enabling

```
User wears earbuds, ANC is ON, listening to music
   │
User speaks to a colleague
   │
FB mic detects voice → ANC pauses → transparency engages (100 ms transition)
   │
User hears surroundings + own voice naturally
   │
User stops speaking → 3 seconds silence → ANC re-engages automatically
```

---

## Verification Steps

1. Enable flag and rebuild
2. Flash to test bud, verify ANC is ON
3. Speak a sentence aloud — confirm transparency engages within ~100 ms
4. Stop speaking — confirm ANC re-engages after hold period (~3–5 s)
5. Test in a room with background conversation — confirm no false triggers at medium threshold
6. Verify call audio is unaffected (speak-to-chat should not trigger during HFP active call)

---

## Related
- [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md) — Section 2
- [→ AUDIO-IMP-004 Wind Noise Detection](./AUDIO-IMP-004%20—%20Wind%20Noise%20Detection.md) — Same ANC mode-switch infrastructure
- [→ GUI TAB 07 — ANC Config](../../SDK%20UPDATE%20FIXING/GUI%20DOCUMENTATION/TAB%2007%20—%20ANC%20Config.md)
- [→ IN-EAR DETECTION](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/IN-EAR%20DETECTION.md) — FB mic is shared with in-ear detection logic; verify no conflict
