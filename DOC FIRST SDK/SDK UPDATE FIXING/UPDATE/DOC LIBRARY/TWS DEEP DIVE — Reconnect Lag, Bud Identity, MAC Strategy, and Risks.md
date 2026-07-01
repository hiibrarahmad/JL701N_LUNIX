---
tags: [tws, reconnect, sync, mac, identity, sibling, ble, edr]
date: 2026-04-27
board: JL7016G Hybrid
chip: AC701N (BR28)
status: Documentation only - no code changes
---

# TWS DEEP DIVE - Reconnect Lag, Bud Identity, MAC Strategy, and Risks

## Scope

This document explains four things in one place:

1. Why TWS can reconnect slowly after a bud leaves the charger/case.
2. Why one bud can sometimes lag behind the other and produce temporary playback mismatch.
3. How this SDK decides which bud belongs to which TWS pair.
4. What MAC address changes can and cannot guarantee in a multi-bud environment.

This is a documentation study only. No code change is applied here.

---

## 1) Current TWS Architecture Assumption

This SDK is a classic two-bud TWS model.

It assumes:
- one local bud
- one sibling bud
- one phone-side relationship

Important technical consequence:

The software does not model an open mesh of many earbuds. It stores one sibling identity and manages one master/slave relationship.

Key anchors:
- `tws_api_get_role()` returns only master or slave role
- `CFG_TWS_REMOTE_ADDR` stores only one sibling address
- `CFG_TWS_LOCAL_ADDR` stores only one local address
- `CFG_TWS_COMMON_ADDR` stores one shared/common identity value

So if many buds are nearby, the firmware is not trying to manage a set of siblings. It is trying to find one valid sibling.

---

## 2) Why Reconnect Can Feel Slow After Charger Removal

The reconnect path is multi-stage.

### Stage 1 - Bud wakes and restores local state

The bud must first leave charger/case-related state and restore radio/app context.

### Stage 2 - TWS reconnect policy runs

The reconnect path uses alternating connect/connectable behavior in `bt_tws_connect_and_connectable_switch()`.

This matters because the system is not always doing the same thing every millisecond. Depending on timing, it may be:
- trying to reconnect to the phone
- trying to reconnect to sibling
- exposing itself as discoverable/connectable

That is why the same physical action can feel different from one attempt to another.

### Stage 3 - Link re-establishes, but audio is still not ready

Even after the sibling link is back:
- buffers must refill
- sequence alignment must be re-established
- slave side must pop good frames again

Only then does stable playback resume.

---

## 3) Why One Bud Can Lag Behind the Other

This is the user symptom you described: one bud resumes “in real time” first, while the other is temporarily behind or mismatched.

### 3.1 Buffer underrun / refill asymmetry

Relevant anchors:
- `tws_api_local_media_trans_push()`
- `tws_api_local_media_trans_pop()`
- `tws_api_auto_drop_frame_enable()`

What happens:
- master side may already have resumed good frames
- slave side may still be draining, refilling, or dropping frames

Result:
- one side sounds live first
- the other catches up slightly later

### 3.2 Auto-drop tradeoff

The TWS media path can enable automatic frame drop during underrun handling.

Tradeoff:
- if auto-drop is enabled, slave can skip stale frames and catch up faster, but may produce audible jumps
- if auto-drop is disabled, slave may pause longer waiting for clean alignment

Either way, the mismatch is a synchronization policy artifact, not necessarily a hardware fault.

### 3.3 Reconnect does not mean instant playback lock

A TWS link being “connected” is not the same as both DAC outputs being perfectly synchronized at that exact instant.

There are separate milestones:
- sibling ACL link alive
- frames arriving
- decoder state valid
- buffer threshold met
- output running in sync

---

## 4) How the SDK Decides Which Bud Belongs to Which Pair

The pair relationship is not based on “any bud with similar name”. It uses stored identity information.

### 4.1 Pair code

`bt_get_tws_device_indicate()` returns a TWS device pairing code.

This code is used during sibling search:
- `bt_tws_search_sibling_and_pair()` calls search by code

Meaning:
- the firmware is not pairing blindly with random nearby devices
- it first searches using the expected pair identity

### 4.2 Stored sibling address

The SDK persists:
- local address
- remote sibling address
- common/shared address

So the reconnect path is strongly tied to the stored sibling record, not just live discovery.

### 4.2.1 Direct answer - does it store sibling address or search fresh every time?

It stores the sibling identity persistently.

This SDK does **not** behave like a fully fresh search-only system after every reboot or every case removal.

The normal model is:

1. first pair/search establishes the sibling relationship
2. the relationship is written into syscfg/VM
3. later reconnects use the remembered sibling identity

Relevant persistent records:
- `CFG_TWS_LOCAL_ADDR` = local bud address
- `CFG_TWS_REMOTE_ADDR` = sibling bud address
- `CFG_TWS_COMMON_ADDR` = common/shared TWS address record

Concrete code anchors:
- `syscfg_id.h` defines `CFG_TWS_LOCAL_ADDR = 95`, `CFG_TWS_REMOTE_ADDR = 96`, `CFG_TWS_COMMON_ADDR = 97`
- `bt_tws.c` reads `CFG_TWS_REMOTE_ADDR` through `tws_get_sibling_addr()`
- `app_chargestore.c` also reads and writes `CFG_TWS_REMOTE_ADDR` during case/charge identity synchronization

So the answer is:

- **first establishment** may use pair-code-based search
- **later reconnects** rely on the stored sibling address and related persistent identity records

This is exactly why stale VM/syscfg data can cause wrong reconnect behavior even when radio conditions are good.

### 4.3 Charge case can reinforce identity persistence

Chargestore logic also stores identity-related data such as device indication and address relationships.

If these records are healthy, reconnect finds the intended sibling faster.

If they are stale/corrupted, you can get:
- delayed reconnect
- wrong sibling search target
- channel confusion
- pair formation failure until clean reset/re-pair

---

## 5) What MAC Address Changes Actually Do

There are multiple identities in play.

### 5.1 EDR / classic BT MAC

This is the main Bluetooth identity used in the classic stack.

It influences:
- phone pairing identity
- TWS-related address storage
- derived identities in some flows

### 5.2 BLE MAC

After FIX-005, BLE MAC can be explicitly read from `CFG_BLE_MAC_ADDR` and applied at boot.

Important limitation:

Changing BLE MAC alone does not define TWS sibling ownership.

BLE identity helps with BLE-side uniqueness, but the TWS sibling model relies primarily on the stored TWS/local/remote/common address relationship and pair code.

### 5.3 Common misconception

Misconception:
- “If I give each bud its own MAC, the pair routing problem is solved.”

Reality:
- unique MACs are necessary for clean identity management
- but they are not sufficient by themselves to define sibling trust and reconnect policy

What really matters in this SDK:
- correct local MAC
- correct sibling MAC
- correct common address relationship
- correct TWS pair code
- clean persisted NVRAM state

---

## 6) What Happens If Many Buds Are Nearby

This SDK is not designed as a multi-bud pool manager.

In a room with many buds:
- each bud still only wants one sibling
- each bud only stores one sibling address record
- the pair code narrows discovery
- persisted address history further narrows reconnect target

So the system is fundamentally “one sibling only”.

That is good for product stability, but it means manufacturing and identity provisioning must be clean.

If provisioning is sloppy:
- wrong pair code reuse
- duplicate addresses
- stale sibling addresses
- erased/unclean VM state

then nearby units can interfere with intended pairing behavior.

---

## 7) Real Risks in the Current TWS Product Experience

### Risk A - One bud reconnects first, audio mismatch follows

Root cause:
- reconnect success and playback-ready timing are not identical between buds

Impact:
- one side resumes first
- user hears temporary lag or mismatch

### Risk B - Reconnect target is correct, but too slow

Root cause:
- alternating connect/connectable windows + wake timing + buffer restart

Impact:
- TWS eventually works, but the user experiences sluggishness after charger removal

### Risk C - Identity data corruption causes bad sibling search

Root cause:
- `CFG_TWS_REMOTE_ADDR`, pair code, or common address relationship not clean

Impact:
- long reconnect attempts
- failed sibling attachment
- apparent random pair behavior

### Risk D - Changing only BLE MAC creates false confidence

Root cause:
- BLE MAC and TWS sibling identity are not the same layer

Impact:
- product appears uniquely identified in BLE, yet TWS behavior is still wrong if TWS records are stale or mismatched

### Risk E - Large nearby bud population increases manufacturing sensitivity

Root cause:
- pair logic is one-sibling-only and depends on correct persisted identity

Impact:
- production must guarantee clean unique identities and clean pairing-state initialization

---

## 8) Improvement Directions

These are safe documentation recommendations, not code changes.

### Improvement 1 - Define a formal identity provisioning policy

For each manufactured pair, explicitly control:
- EDR MAC uniqueness
- BLE MAC uniqueness
- TWS pair code
- clean initial VM/NVRAM state

This is the most important non-code improvement.

### Improvement 2 - Separate “pair identity” from “advertising identity” in documentation

Document clearly for the team:
- BLE MAC is not the full TWS sibling identity
- TWS sibling relation depends on stored local/remote/common addressing and pair code

### Improvement 3 - Add reconnect timing instrumentation

Recommended timestamps:
- charger removal detected
- wake complete
- sibling search start
- sibling link up
- first clean media frame
- audio output stable

This tells you exactly where the lag comes from.

### Improvement 4 - Review auto-drop frame policy under real RF conditions

If the user complaint is mainly “one bud lags for a moment”, then the right tuning target is media sync/buffer policy, not random RF or MAC changes.

### Improvement 5 - Define factory recovery flow

For field/service use, define a clean reset method that reinitializes:
- sibling address records
- pair code state if needed
- VM/persistent pairing data

This is essential when units are swapped, repaired, or mis-paired in test environments.

---

## 9) Clear Answer to the Multi-Bud Question

If many buds are present, this firmware does not dynamically manage a large family of sibling candidates.

It is designed to reconnect to one dedicated sibling.

The best guarantee that each bud returns to its intended sibling is not “just change MAC” by itself. The correct guarantee is:

1. each unit has unique classical and BLE identity
2. each intended pair has the correct TWS pair code
3. each bud stores the correct sibling address records
4. VM/NVRAM is clean during provisioning and recovery

That is the real pairing contract in this SDK.

---

## 10) Related Files

- apps/earphone/bt_tws.c
- include_lib/btctrler/classic/tws_api.h
- include_lib/btctrler/classic/tws_local_media_sync.h
- cpu/br28/audio_dec/audio_dec_file.c
- apps/earphone/user_cfg.c
- include_lib/system/syscfg_id.h
- apps/earphone/power_manage/app_chargestore.c
- apps/earphone/earphone.c
- FIX-005 — BLE MAC Address Ignored at Boot

---

## Related FIX Records

| Fix | Title | Relevance |
|-----|-------|-----------|
| [FIX-004](../../FIXING/FIX-004%20—%20TWS%20auto%20pairing%20and%20PC5%20channel%20select%20validation.md) | TWS auto pairing + PC5 channel select | Initial TWS bring-up |
| [FIX-014](../../FIXING/FIX-014%20—%20TWS%20not%20seamless%20under%20MAC%20profile%20and%20PC5%20bias%20requirement.md) | TWS seamless reconnect issue | Reconnect lag / race condition |
| [FIX-020](../../FIXING/FIX-020%20—%20TWS%20Volume%20Desync%20Between%20Buds.md) | TWS volume desync | Volume sync path (`tws_api_send_data_to_sibling`) |
| [FIX-021](../../FIXING/FIX-021%20—%20Per-Bud%20Key%20Table%20Split%20Does%20Not%20Work%20in%20TWS.md) | Compile-time key table splits ineffective | TWS master-owns-all architecture |
| [FIX-022](../../FIXING/FIX-022%20—%20Right%20Bud%20Vol%20Up%20Left%20Bud%20Vol%20Down%20Channel-Aware%20Dispatch.md) | Per-bud channel-aware key dispatch | Runtime L/R differentiation |
