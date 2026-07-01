---
tags: [architecture, design-decisions, rationale, adr]
date: 2026-05-05
---

# Design Decisions — JL7016G Hybrid SDK

This document records architectural and design decisions made during the JL7016G Hybrid bring-up. Each entry explains **what was decided**, **why**, and **what would happen if you reversed it**. The goal is to prevent future developers from accidentally "fixing" intentional choices.

---

## DD-001 — PB1 (CH1) is GPIO-Output Only; No App Key Events

**Decision:** PB1 (Port B pin 1, CTMU CH1) does not generate app-level key events. Its only function is to drive PC3 HIGH/LOW to reflect touch state. Key events from CH1 are suppressed inside `lp_touch_key.c`.

**Why:**
- PB1 is the in-ear detection pad, not a user gesture pad
- If PB1 fired key events, every time the bud was inserted into the ear it would trigger play/pause, next track, or power-off
- The hardware requires a clean digital output on PC3 to signal "bud in ear" to downstream logic; this needs no app involvement

**FIX Records:** [FIX-015](../FIXING/FIX-015%20—%20PB1_COMPLETE_SOLUTION.md), [FIX-018](../FIXING/FIX-018%20—%20PB1%20Key%20Events%20Suppressed%20GPIO%20Only.md)

**If you reverse this:** Every ear insertion will trigger unintended media/call actions. The PC3 GPIO output will also still fire (it runs in the same CTMU handler), causing confusing dual behaviour.

---

## DD-002 — PC3 is Active-LOW (Idle HIGH, Touch LOW)

**Decision:** PC3 is driven HIGH at boot (idle state) and driven LOW when PB1 is touched. This is active-LOW logic.

**Why:**
- The downstream hardware connected to PC3 requires a LOW signal to detect "bud in ear"
- Active-LOW is also the conventional choice for "detection active" signals on most hardware designs (pulled up by default, pulled down to signal an event)
- Changed from active-HIGH in [FIX-019](../FIXING/FIX-019%20—%20PC3%20Polarity%20Inverted%20(Active%20LOW).md) when the downstream hardware requirement was confirmed

**Config note:** Can alternatively be changed by setting `TCFG_LP_TOUCH_PB1_LED_ACTIVE_LEVEL 0` in `board_jl7016g_hybrid_cfg.h` rather than editing `lp_touch_key.c` directly.

**If you reverse this:** PC3 will be LOW at idle and HIGH on touch — downstream logic will see "bud in ear" at all times and "bud out" only when touched.

---

## DD-003 — TWS Master Evaluates Its Own Key Table for All Events

**Decision:** Only the master bud runs `app_earphone_key_event_handler()`. The slave forwards raw touch events to the master via the TWS link with `arg = KEY_EVENT_FROM_TWS`. The master looks up its own `key_table[]` for every event — including forwarded slave events.

**Why:**
- This is the JieLi SDK architectural design; it cannot be changed without modifying the TWS core
- The master is the only bud with a live BT Classic connection to the phone; it must be the one to send AVRCP commands
- Having both buds independently execute key actions would cause double commands (play/pause fired twice, volume changed twice)

**Consequence:** Compile-time `#if TCFG_RIGHT_BUD` splits in `key_table[]` rows are **ineffective**. The master's table wins for both physical buds. Documented in [FIX-021](../FIXING/FIX-021%20—%20Per-Bud%20Key%20Table%20Split%20Does%20Not%20Work%20in%20TWS.md).

**Correct approach:** Use `key_tws_lr_diff_deal()` at runtime to inspect `tws_api_get_local_channel()` and `event->arg` to determine which physical bud was touched. Implemented in [FIX-022](../FIXING/FIX-022%20—%20Right%20Bud%20Vol%20Up%20Left%20Bud%20Vol%20Down%20Channel-Aware%20Dispatch.md).

**If you reverse this:** No runtime change occurs (the TWS layer enforces this), but adding per-bud key table splits will create confusing dead code that appears to work in standalone mode but breaks in TWS.

---

## DD-004 — Single Firmware Image for Both Buds

**Decision:** One firmware binary is built and flashed to both the left and right bud. The bud identity (Left / Right) is determined at runtime by:
1. The MAC address provisioned via `user_cfg.c` (different per bud)
2. The PC5 hardware channel select pin (hardware distinction)
3. `tws_api_get_local_channel()` at runtime (returns `'L'` or `'R'`)

**Why:**
- Maintaining two separate firmware builds per-release doubles the build and QA overhead
- Compile-time per-bud splits are ineffective in TWS anyway (see DD-003)
- Runtime detection via `tws_api_get_local_channel()` is available and reliable

**If you reverse this (use two builds):** Any compile-time difference only affects single-bud standalone behaviour. In TWS mode, the master's firmware governs everything regardless of which build the slave bud has.

---

## DD-005 — AVRCP Round-Trip is the Only Active Volume Path During Key Presses

**Decision:** `volume_up()` and `volume_down()` send `USER_CTRL_CMD_SYNC_VOL_INC/DEC` (AVRCP path through the phone) but do **not** call `bt_tws_sync_volume()` (direct TWS data channel push). `bt_tws_sync_volume()` is only called at connection events (connect, A2DP start).

**Why:**
- Adding `bt_tws_sync_volume()` inside `volume_up/down()` — alongside the existing AVRCP path — caused **volume oscillation** during HOLD repeat events
- The two paths calculate volume independently and fight each other: the TWS push sets the peer to level N, then the phone's AbsoluteVolume response sets both buds to level M, where M ≠ N if phone and bud were out of sync
- On every HOLD repeat (~500 ms), the buds alternate between levels N and M, producing audible back-and-forth oscillation
- Removing the in-key-press TWS push eliminates the oscillation; the AVRCP path handles synchronisation via the phone

**FIX Records:** [FIX-022](../FIXING/FIX-022%20—%20Right%20Bud%20Vol%20Up%20Left%20Bud%20Vol%20Down%20Channel-Aware%20Dispatch.md)

**If you reverse this (add `bt_tws_sync_volume()` back to `volume_up/down()`):** Volume oscillation will return whenever HOLD repeat events fire rapidly.

---

## DD-006 — Manual MAC Provisioning via `user_cfg.c` Comment Block

**Decision:** Bud identity (Left/Right MAC address) is provisioned by manually uncommenting a single function call inside `user_cfg.c` before flashing. No automatic provisioning or runtime selection.

**Why:**
- The JieLi SDK does not provide a safe runtime mechanism to write MAC addresses after production — MAC provisioning can only be done during the factory flash cycle
- A single manual comment/uncomment is the simplest approach with zero risk of both buds getting the same MAC
- The `#if TCFG_MANUAL_MAC_PROVISIONING_ENABLE` guard prevents accidental double-provisioning

**Consequence:** The `user_cfg.c` file must be edited (and the correct line uncommented) before building and flashing each bud. Different binary per bud — but only in the provisioning block, not in key logic.

**If you reverse this:** Both buds will use the default factory MAC from the Config GUI, which is the same for both buds. TWS will fail — buds cannot pair with each other if they share a MAC address.

---

## DD-007 — `tws_api_send_data_to_sibling` for Volume Sync

**Decision:** `bt_tws_sync_volume()` uses `tws_api_send_data_to_sibling` (not `tws_api_send_data_to_slave`).

**Why:**
- `tws_api_send_data_to_slave` only sends from master → slave. A slave calling it is a no-op (no peer to send to in "slave" direction)
- Volume level changes happen from either bud. The sync function must work regardless of which bud calls it
- `tws_api_send_data_to_sibling` routes to whichever peer is connected, regardless of role

**FIX Records:** [FIX-020](../FIXING/FIX-020%20—%20TWS%20Volume%20Desync%20Between%20Buds.md)

**If you reverse this:** Volume changes initiated on the slave bud will never reach the master bud's DAC, causing the buds to play at different volume levels until the phone sends an AbsoluteVolume update.

---

**Back to:** [→ ARCHITECTURE/](./README.md) | [→ Main Documentation Hub](../README.md)
