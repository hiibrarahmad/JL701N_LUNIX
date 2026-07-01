---
tags: [connection, bluetooth, pbap, phonebook, caller-id, profile, jl7016g, improvement]
date: 2026-06-08
status: PLANNED — NOT IMPLEMENTED
effort: 🟢 Low
risk: ✅ Safe — additive profile, does not affect audio
priority: 9 — Low effort, low-medium impact (caller ID + contacts)
---

# 📡 CONN-IMP-003 — PBAP Phone Book Access Profile

> **One-line summary:** Enable PBAP so the earphone can retrieve contact names from the paired phone — allowing caller ID to display contact names via voice announcement rather than raw phone numbers.

---

## Current State

PBAP is **disabled**:

```c
// board_jl7016g_hybrid_cfg.h
#define USER_SUPPORT_PROFILE_PBAP    0   // Phone Book Access Profile off
```

Without PBAP, when an incoming call arrives:
- The HFP profile delivers the caller's phone number
- No contact name is available — the earphone can only announce the number (or a generic "incoming call" tone)
- Some phones push the contact name via HFP Clip extension, but this is not universal

---

## What PBAP Adds

| Feature | Without PBAP | With PBAP |
|---|---|---|
| Incoming call display | Phone number only | Contact name (if in phonebook) |
| Voice announcement | "Incoming call from 07712345678" | "Incoming call from John Smith" |
| Call history sync | No | Yes (if SDK supports vCard parsing) |
| Recent contacts | No | Yes |

### PBAP Pull Flow

```
Phone pairs → PBAP server active on phone
Earphone → PBAP client → request vCard for incoming number
                        → phone returns "John Smith"
                        → earphone TTS: "Incoming call from John Smith"
```

---

## Recommended Change

```c
// board_jl7016g_hybrid_cfg.h
#define USER_SUPPORT_PROFILE_PBAP    1   // was 0
```

### SDK Dependency

PBAP caller name announcement also requires the Text-to-Speech (TTS) or name-reading feature to be configured. In the JL7016G SDK this is typically tied to:
- The tone file engine (WTG/WTS format)
- Or a phone-side push (the phone sends name via AT+CLIP extended)

Check the `apps/earphone/earphone.c` HFP handler for `hfp_caller_number_notify` and `hfp_caller_name_notify` — if name handling is already stubbed, enabling PBAP will populate it.

---

## Risk & Trade-offs

| Aspect | Assessment |
|---|---|
| Flash cost | PBAP client library: ~4–8 KB — negligible |
| Phone permission required | Android requires user to grant "phonebook access" on pairing — one-time prompt |
| Privacy concern | Phonebook is pulled by earphone — data stays local, not transmitted elsewhere |
| Audio path impact | None — PBAP is a separate ACL data channel |
| iOS compatibility | iOS restricts PBAP access; name push via AT+CLIP is more reliable on iOS |
| Reversible | Yes — set `0` to disable |

---

## Verification Steps

1. Enable flag and rebuild
2. Flash to test bud and pair with Android phone
3. On first connect: Android shows "Allow [Earphone] to access your contacts?" → Accept
4. Have another phone call the paired phone
5. Confirm: UART log shows PBAP pull request for the incoming number
6. If TTS name announcement is configured: verbal name announcement plays
7. If not yet configured: confirm at minimum the contact name is received (log it)

---

## Related
- [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md) — Section 5
- [→ GUI TAB 01 — BT Config](../../SDK%20UPDATE%20FIXING/GUI%20DOCUMENTATION/TAB%2001%20—%20BT%20Config.md)
- [→ CONN-IMP-002 SPP Profile](./CONN-IMP-002%20—%20SPP%20Profile%20Enable.md) — Enable alongside SPP for richer app integration
- [→ BT_CONFIG Structure](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/BT_CONFIG%20-%20Bluetooth%20Configuration%20Structure.md)
