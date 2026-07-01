---
tags: [backlog, todo, known-issues, future-work]
date: 2026-05-05
---

# TODO Backlog — JL7016G Hybrid SDK

This document consolidates all known unresolved issues, disabled features, and planned improvements. Items are grouped by subsystem.

> **Legend:**
> - 🔴 HIGH — broken or impairs basic product function
> - 🟡 MEDIUM — degrades user experience but has workaround
> - 🟢 LOW — improvement or optional feature
> - 📝 DOC — documentation-only task

---

## 🔴 HIGH — Active Bugs / Blockers

### BL-001 — FIX-014: TWS Seamless Reconnect Not Fully Resolved

**Problem:** After power-cycling both buds and powering on the left bud first, there is a ~3–5 second window where the left bud connects to the phone as a standalone device before the right bud connects. During this window, if audio is playing, the right bud can fail to rejoin the TWS pair cleanly. The result is one bud playing and one silent, requiring a manual reconnect.

**Current status:** [FIX-014](./FIXING/FIX-014%20—%20TWS%20not%20seamless%20under%20MAC%20profile%20and%20PC5%20bias%20requirement.md) — IN PROGRESS

**Known contributing factors:**
- PC5 bias voltage on the right bud affects TWS channel negotiation timing
- The `user_cfg.c` sibling MAC must match the currently paired MAC on each bud

**Next steps:**
- [ ] Investigate `TCFG_TWS_CONNECT_TIMEOUT` setting
- [ ] Log the BT stack state on both buds simultaneously during the race condition
- [ ] Test with explicit reconnect policy forcing TWS-first connect before BT Classic

---

## 🟡 MEDIUM — Disabled Features (Hardware Present, Feature Off)

### MD-001 — In-Ear Detection Hardware Disabled

**Problem:** The hardware (PB1 / CH1 capacitive pad) is physically present and operational — PB1 is actively generating touch signals routed to PC3 GPIO. However, the SDK-level in-ear detection logic (`app_earphone_ear_detect`) is disabled.

**Config:** `TCFG_EAR_DETECT_ENABLE = DISABLE` in `board_jl7016g_hybrid_cfg.h`

**Impact:** Auto-pause when bud removed from ear is not active. Auto-resume when bud reinserted is not active.

**Blocker:** The application-level in-ear detect uses the same CTMU channel as PB1 touch. With PB1 configured as GPIO-output only (FIX-018), enabling `TCFG_EAR_DETECT_ENABLE` may conflict. Needs investigation before enabling.

**Next steps:**
- [ ] Determine if `app_earphone_ear_detect` can consume PC3 GPIO state (already computed by `lp_touch_key.c`) instead of re-running CTMU measurement
- [ ] Enable and test on bench before deploying

---

### MD-002 — Keyword Spotting (KWS) Voice Assistant Disabled

**Problem:** The BR28 DSP supports an always-on keyword spotting engine for voice wake-word detection ("Hey Siri" / "OK Google" style). This is disabled on JL7016G Hybrid.

**Config:** `TCFG_SMART_VOICE_ENABLE = DISABLE_THIS_MOUDLE`

**Why disabled:** The KWS engine competes for DSP resources with ANC. Enabling both simultaneously on this hardware profile caused instability during bring-up. ANC was prioritised.

**Next steps:**
- [ ] Investigate whether JieLi's KWS + ANC co-existence mode is available in this SDK version
- [ ] If not, document as a known hardware/SDK resource constraint

---

### MD-003 — Swipe Gesture Support Not Implemented

**Problem:** The PB4 (CH3) touch sensor is capable of detecting directional swipe gestures (the CTMU supports delta-direction detection with two sense points). Currently only discrete single/double/triple tap and hold are implemented.

**Impact:** Users cannot swipe forward/back through a playlist without multiple taps.

**Next steps:**
- [ ] Review `lp_touch_key.c` swipe detection API in JieLi documentation
- [ ] Map swipe-left → next track, swipe-right → previous track

---

## 🟡 MEDIUM — Power Optimisation

### PM-001 — LDO vs DCDC Power Supply

**Problem:** The system is using LDO power regulation (`TCFG_LOWPOWER_POWER_SEL = PWR_LDO15`). LDO is simpler and cleaner but less efficient — it wastes excess voltage as heat.

**Impact:** Reduced battery life compared to DCDC mode, especially during active audio playback.

**Next steps:**
- [ ] Switch `TCFG_LOWPOWER_POWER_SEL = PWR_DCDC15` in `board_jl7016g_hybrid_cfg.h`
- [ ] Test for audio noise / interference introduced by DCDC switching noise on MICBIAS and analog paths
- [ ] If DCDC-induced noise is acceptable, keep; otherwise revert to LDO

---

## 🟢 LOW — Improvements / Nice to Have

### LW-001 — No Audio Tone for L/R Bud Identification

**Feature request:** When both buds are powered on, play a brief "L" or "R" voice prompt tone so the user can identify which bud to insert in which ear.

**Next steps:**
- [ ] Add `tone_table` entry for L/R ident tones
- [ ] Trigger at TWS role establishment (after `tws_api_get_local_channel()` resolves)

---

### LW-002 — Config GUI Name Not Preserved Across OTA

**Problem:** After an OTA firmware update, the custom BT name (set in `user_cfg.c` and Config GUI) is reset to the SDK default. The Config GUI name block in flash is overwritten by the full update package.

**Next steps:**
- [ ] Investigate whether the JieLi OTA partition layout can preserve the user configuration block
- [ ] Alternatively, document that post-OTA BT name must be re-provisioned

---

### LW-003 — No Low Battery Voice Prompt

**Feature request:** No audible warning when battery drops below 10%, 5%, and 2%. Users don't know the bud is about to die.

**Next steps:**
- [ ] Add battery % threshold callbacks in `charge.c` or power_manage module
- [ ] Trigger tone table entries at 10%, 5%, 2%

---

## 📝 DOC — Documentation Tasks

### DT-001 — FIX Backlinks Missing from Deep-Dive Documents

16 deep-dive documents in `UPDATE/DOC LIBRARY/` do not have "Related FIX Records" footers.

**Priority mapping:**
- `TWS DEEP DIVE` → FIX-004, FIX-014, FIX-020, FIX-021, FIX-022
- `AUDIO DEEP DIVE` → FIX-012, FIX-013, FIX-020, FIX-022
- `IN-EAR DETECTION` → FIX-007, FIX-008, FIX-009, FIX-010, FIX-015
- `TOUCH FEEDBACK PLAN` → FIX-016, FIX-018, FIX-019
- `MAIN MIC INTEGRATION` → FIX-012, FIX-013
- `UART LOGGING NOTE` → FIX-011
- `BOARD — JL7016G Config` → FIX-001, FIX-012, FIX-013, FIX-015
- `CONFIG GUI DEEP DIVE` → FIX-005, FIX-006
- `FEATURE AUDIT` → FIX-020, FIX-021, FIX-022

---

### DT-002 — REFERENCE/README.md Does Not Exist

The `REFERENCE/` folder contains several PB1-specific scripts and tools with no index. Add a `README.md` explaining the contents.

---

**Back to:** [→ Main Documentation Hub](../README.md)
