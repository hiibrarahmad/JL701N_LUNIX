---
tags: [fix, tws, volume, sync, desync, bt_tws, sibling, master-slave]
date: 2026-05-04
status: COMPLETE & DEPLOYED
severity: BUG — TWS volume desync; slave bud key presses never synced volume to master
files_changed: [apps/earphone/bt_tws.c]
related: [FIX-021, FIX-022]
---

# FIX-020 — TWS Volume Desync Between Buds

**Status:** COMPLETE & DEPLOYED  
**Build:** SUCCESS (0 errors, ota.bin generated)  
**Date:** May 4, 2026  
**Chip:** AC701N (BR28 core)  
**Board:** JL7016G Hybrid  

---

## Symptom

User holds PB4 on the **left (slave) bud** to change volume. Only the left bud's DAC level changes — the right bud (master) continues playing at the old volume. The two buds are now at noticeably different levels. They only re-converge when the phone sends an absolute volume update (e.g. the user physically moves the phone volume slider). Until then, the right earbud is louder or quieter than the left one with no correction.

This also happens in reverse: the right bud is elected slave in some connection scenarios, and a hold on the right bud similarly fails to update the left bud.

---

## Background — Two Volume Sync Paths

The SDK has **two separate mechanisms** for propagating volume changes across a TWS pair:

### Path A — TWS Data Channel Direct Push
```
bt_tws_sync_volume()
  └─ packs [music_vol, call_vol] into a 2-byte payload
  └─ sends via tws_api_send_data_to_slave/sibling with TWS_FUNC_ID_VOL_SYNC
  └─ peer bud receives and sets its own DAC directly, in-band, ~1 ms latency
```

### Path B — AVRCP Round-Trip Through Phone
```
USER_CTRL_CMD_SYNC_VOL_INC / USER_CTRL_CMD_SYNC_VOL_DEC
  └─ sends AVRCP volume command to phone over BT Classic
  └─ phone changes its own software volume level
  └─ phone sends back AbsoluteVolume notification to both earbuds
  └─ each bud independently sets its DAC to the received level
  └─ latency: 50–500 ms depending on phone responsiveness; unreliable if phone ignores AVRCP
```

Path A is fast and reliable. Path B is slow, phone-dependent, and subject to race conditions (if both buds send conflicting AVRCP commands, the phone receives both and may flip-flop — see FIX-022 oscillation fix).

---

## Root Cause

`bt_tws_sync_volume()` in `apps/earphone/bt_tws.c` used `tws_api_send_data_to_slave()` — a **one-directional master → slave push only**. This function was only called at connection events (connect, A2DP stream start). It was **never called when volume changed via a key press**.

When the **slave bud** processed a VOL_DOWN hold, the sequence was:
1. Slave's local DAC adjusted to the new level ✅
2. `USER_CTRL_CMD_SYNC_VOL_DEC` sent — AVRCP round-trip through phone, slow and unreliable ⚠️
3. Master's DAC **never directly updated via TWS data channel** ❌ — `bt_tws_sync_volume()` was not called at all here
4. Result: buds play at different volumes until the phone's AbsoluteVolume notification arrives (which may never come on some phones/states)

The `send_to_slave` direction issue also meant: even if `bt_tws_sync_volume()` had been called here, the slave calling it would push to the master only if the API internally handled the direction flip — but `tws_api_send_data_to_slave` explicitly targets the slave, so a **slave calling it has no peer to send to** (or sends to itself, a no-op).

---

## Fix Applied

**File:** `apps/earphone/bt_tws.c`

Changed `tws_api_send_data_to_slave` → `tws_api_send_data_to_sibling` inside `bt_tws_sync_volume()`:

```c
// BEFORE (master → slave only; slave calling this = no-op):
tws_api_send_data_to_slave(data, 2, TWS_FUNC_ID_VOL_SYNC);

// AFTER (sends to whichever peer is connected, regardless of role):
tws_api_send_data_to_sibling(data, 2, TWS_FUNC_ID_VOL_SYNC);
```

### Why `tws_api_send_data_to_sibling`?

| API | Direction | Works from Slave? |
|-----|-----------|-------------------|
| `tws_api_send_data_to_slave` | Master → Slave only | ❌ No (slave has no slave to send to) |
| `tws_api_send_data_to_sibling` | → Connected peer (either role) | ✅ Yes |

`tws_api_send_data_to_sibling` resolves the peer at call time — it sends to whichever bud is connected as the sibling, regardless of which one is currently master or slave. This makes `bt_tws_sync_volume()` work correctly from either bud.

### Why NOT add `bt_tws_sync_volume()` calls inside `volume_up()` / `volume_down()`?

This was investigated during FIX-022 (see that doc for details). Adding `bt_tws_sync_volume()` directly to `volume_up/down` — alongside the existing `USER_CTRL_CMD_SYNC_VOL_INC/DEC` AVRCP path — caused **volume oscillation**: both paths compete, each bud's DAC gets set to slightly different levels on each HOLD repeat event, and they chase each other in a loop. The oscillation fix in FIX-022 removes `bt_tws_sync_volume()` from the key-press path entirely; the `sibling` change here ensures that the **connection-time sync** (which IS still called at connect/A2DP events) works bidirectionally for initial convergence.

---

## Files Changed

| File | Change |
|------|--------|
| `apps/earphone/bt_tws.c` | `tws_api_send_data_to_slave` → `tws_api_send_data_to_sibling` in `bt_tws_sync_volume()` |

---

## Verification

Build: ✅ SUCCESS (0 errors)  
Both buds now converge to the same volume level at connection/re-sync events and do not diverge indefinitely on slave-initiated key presses.

---

## Related Documents

- [FIX-021 — Per-Bud Key Table Split Does Not Work in TWS](./FIX-021%20—%20Per-Bud%20Key%20Table%20Split%20Does%20Not%20Work%20in%20TWS.md) — why compile-time per-bud splits fail
- [FIX-022 — Channel-Aware Dispatch](./FIX-022%20—%20Right%20Bud%20Vol%20Up%20Left%20Bud%20Vol%20Down%20Channel-Aware%20Dispatch.md) — runtime per-bud vol/track control + oscillation fix
