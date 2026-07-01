# Feature Audit — Playback Controls, Call Controls, Volume, Voice Assistant, In-Ear Detection
**Date:** 2026-04-22  
**Chip:** AC701N (BR28 core)  
**Board:** JL7016G Hybrid  
**Audit Scope:** SDK code-level verification — no code was changed. Read-only investigation only.  

---

## Summary Table

| Feature                              | Code Present | Config Gate                          | Status on JL7016G Hybrid | Notes                                                                                           |
| ------------------------------------ | ------------ | ------------------------------------ | ------------------------ | ----------------------------------------------------------------------------------------------- |
| Play / Pause                         | ✅ YES        | Always compiled                      | ✅ ACTIVE                 | `KEY_MUSIC_PP` → `USER_CTRL_AVCTP_OPID_PLAY`                                                    |
| Answer Incoming Call                 | ✅ YES        | Always compiled                      | ✅ ACTIVE                 | Same `KEY_MUSIC_PP` branches to `USER_CTRL_HFP_CALL_ANSWER`                                     |
| Hang Up / Reject Call                | ✅ YES        | Always compiled                      | ✅ ACTIVE                 | `KEY_MUSIC_PP`, `KEY_POWEROFF`, `KEY_MUSIC_NEXT/PREV` all branch to `USER_CTRL_HFP_CALL_HANGUP` |
| Volume Up                            | ✅ YES        | Always compiled                      | ✅ ACTIVE                 | `KEY_VOL_UP` → `volume_up()` — syncs across TWS (FIX-020); KEY_2 hold is channel-aware (FIX-022) |
| Volume Down                          | ✅ YES        | Always compiled                      | ✅ ACTIVE                 | `KEY_VOL_DOWN` → `volume_down()` — syncs across TWS; KEY_2 left-bud hold dispatches `volume_down()` via channel detection |
| Per-Bud Vol+Next / Vol-Prev (KEY_2)  | ✅ YES        | `TCFG_USER_TWS_ENABLE`, `ONE_KEY_CTL_DIFF_FUNC` | ✅ ACTIVE      | Right bud HOLD=VolUp/DoubleTap=Next, Left bud HOLD=VolDown/DoubleTap=Prev — runtime channel detection, single firmware |
| Open Voice Assistant (Siri / Google) | ✅ YES        | Always compiled                      | ✅ ACTIVE                 | `KEY_OPEN_SIRI` → `USER_CTRL_HFP_GET_SIRI_OPEN` via HFP AT command                              |
| Wake-Word Voice Assistant (KWS)      | ✅ YES        | `TCFG_KWS_VOICE_EVENT_HANDLE_ENABLE` | ❌ DISABLED               | `TCFG_SMART_VOICE_ENABLE = DISABLE_THIS_MOUDLE` on this board                                   |
| In-Ear Detection — App Logic         | ✅ YES        | `TCFG_EARTCH_EVENT_HANDLE_ENABLE`    | ✅ COMPILED IN            | App logic compiled, but hardware sensor must be wired                                           |
| In-Ear Detection — Hardware Power    | ✅ YES        | `TCFG_EAR_DETECT_ENABLE`             | ❌ DISABLED               | External touch/in-ear power supply disabled for this board                                      |

---

## 1. Play / Pause

### Code Location
- `apps/earphone/key_event_deal.c` — `case KEY_MUSIC_PP:`

### How It Works
The `KEY_MUSIC_PP` key action is context-aware. The handler checks the current call status before deciding what to do:

```
If call status == BT_CALL_OUTGOING or BT_CALL_ALERT  → HFP HANGUP (cancel outgoing)
If call status == BT_CALL_INCOMING                   → HFP ANSWER
If call status == BT_CALL_ACTIVE                     → HFP HANGUP
Else (no call)                                       → AVCTP PLAY (play/pause toggle)
```

The AVCTP PLAY opid is `USER_CTRL_AVCTP_OPID_PLAY` sent via `user_send_cmd_prepare()`.

### Status: FULLY IMPLEMENTED AND ACTIVE
No configuration gate blocks this. It is always active whenever a key is mapped to `KEY_MUSIC_PP` in the key table.

---

## 2. Answer Call

### Code Location
- `apps/earphone/key_event_deal.c` — inside `case KEY_MUSIC_PP:` at line ~389
- Command: `USER_CTRL_HFP_CALL_ANSWER`

### How It Works
When `KEY_MUSIC_PP` fires and the call state is `BT_CALL_INCOMING`, it sends `USER_CTRL_HFP_CALL_ANSWER`. This triggers the HFP stack to accept the incoming call.

There is also a dedicated case `KEY_CALL_ANSWER` in the switch, but that case currently has **no body** (empty handler). The actual answer logic lives inside `KEY_MUSIC_PP`.

### Status: FULLY IMPLEMENTED AND ACTIVE

---

## 3. Hang Up / Cut Off Call

### Code Location
- `apps/earphone/key_event_deal.c` — multiple places
- `KEY_MUSIC_PP` — hangup if call is active or outgoing (line 387, 391)
- `KEY_POWEROFF` — hangup if incoming or active call (lines 407, 414, 419)
- `KEY_MUSIC_NEXT` / `KEY_MUSIC_PREV` — hangup during phone call (lines 474, 494, 503, 580, 586)
- Dedicated case `KEY_CALL_HANG_UP` — empty body (not routed, reserved only)
- Command: `USER_CTRL_HFP_CALL_HANGUP`

### How It Works
`USER_CTRL_HFP_CALL_HANGUP` is sent via `user_send_cmd_prepare()` which routes through the HFP profile to send the AT+CHUP (or AT+CHLD) command to the connected phone.

### Status: FULLY IMPLEMENTED AND ACTIVE  
Note: The dedicated `KEY_CALL_HANG_UP` case is empty — it is a leftover stub. Actual hangup is wired through `KEY_MUSIC_PP` and `KEY_POWEROFF`.

---

## 4. Volume Up / Volume Down (KEY_2 — Per-Bud Channel-Aware)

### Code Location
- `apps/earphone/key_event_deal.c` — `case KEY_VOL_UP:` and `case KEY_MUSIC_NEXT:`
- `lr_diff_otp_deal()` and `key_tws_lr_diff_deal()` in the same file
- `bt_tws_sync_volume()` in `apps/earphone/bt_tws.c`

### How It Works — Per-Bud Differentiation (FIX-022)
KEY_2 (PB4, `key_value = 2`) HOLD maps to `KEY_VOL_UP` in the key table, but the handler intercepts it when TWS is connected:

```
case KEY_VOL_UP:
    if key->value == 2 AND tws connected:
        key_tws_lr_diff_deal() → lr_diff_otp_deal(VOL_UP_DOWN)
            Right bud touched → volume_up(1)
            Left  bud touched → volume_down(1)
    else:
        volume_up(1)   ← KEY_1 HOLD or standalone
```

KEY_2 DOUBLE_TAP maps to `KEY_MUSIC_NEXT`, similarly intercepted:
```
case KEY_MUSIC_NEXT:
    if key->value == 2 AND tws connected:
        key_tws_lr_diff_deal() → lr_diff_otp_deal(NEXT_PREV)
            Right bud touched → AVCTP_OPID_NEXT
            Left  bud touched → AVCTP_OPID_PREV
    else:
        existing NEXT logic
```

**Channel resolution** in `key_tws_lr_diff_deal()`:
- Asks `tws_api_get_local_channel()` — which L/R channel is this master?
- Checks `event->arg == KEY_EVENT_FROM_TWS` — was this event forwarded from the peer?
- Combines both facts to determine which physical bud was touched.

### How It Works — volume_up() / volume_down()
`volume_up()` is fully context-aware:
1. **During incoming call:** Adjusts volume directly (bypass tone check)
2. **During call (active or outgoing):** Adjusts HFP call volume
3. **Max volume already reached:** Plays max-volume tone (TWS-synced), then sends HFP vol up to phone
4. **Music (no call):** Calls `app_audio_volume_up()`, syncs across TWS with `USER_CTRL_CMD_SYNC_VOL_INC`

### TWS Volume Sync (FIX-020)
`bt_tws_sync_volume()` in `bt_tws.c` pushes `[music_vol, call_vol]` to the peer bud via `TWS_FUNC_ID_VOL_SYNC`. After FIX-020 this uses `tws_api_send_data_to_sibling` (bidirectional) instead of `tws_api_send_data_to_slave` (master-only). Called at connect/A2DP-start to re-converge both buds.

### Important SDK Architecture Note (FIX-021)
`#if TCFG_RIGHT_BUD` compile-time splits in `key_table[]` rows have **no effect in TWS**. The master evaluates its own table for all events including forwarded slave touches. Never use compile-time per-bud splits for key table rows — always use `key_tws_lr_diff_deal()` for runtime differentiation.

### Status: FULLY IMPLEMENTED AND ACTIVE
- Volume up/down: always active
- Per-bud direction (KEY_2): active when `TCFG_USER_TWS_ENABLE` and `ONE_KEY_CTL_DIFF_FUNC` are enabled (both enabled on JL7016G Hybrid)
- Standalone (single bud, no TWS): KEY_2 HOLD defaults to Vol Up

---

## 6. Open Voice Assistant (Siri / Google Assistant)

### Code Location
- `apps/earphone/key_event_deal.c` — `case KEY_OPEN_SIRI:` line 540
- Command: `USER_CTRL_HFP_GET_SIRI_OPEN`
- Stack declaration: `include_lib/btstack/avctp_user.h` lines 108-112

### How It Works
Sends `USER_CTRL_HFP_GET_SIRI_OPEN` via `user_send_cmd_prepare()`. This triggers the HFP profile to send the Apple Siri / Google Assistant activation command to the connected phone over the HFP AT+BVRA command. 

The Siri/voice assistant open/close/status lifecycle is:
- `USER_CTRL_HFP_GET_SIRI_STATUS` — query current status
- `USER_CTRL_HFP_GET_SIRI_OPEN` — open voice assistant
- `USER_CTRL_HFP_GET_SIRI_CLOSE` — close voice assistant

`is_siri_open()` is also called in `earphone.c` (lines 1135-1187) to check if the assistant is currently active, so other logic can be blocked while the assistant is open.

### Status: FULLY IMPLEMENTED AND ACTIVE  
Works with both iOS (Siri) and Android (Google Assistant) — same AT+BVRA HFP command works on both platforms.

---

## 7. Wake-Word Voice Assistant (KWS — Keyword Spotting)

### Code Location
- `apps/earphone/kws_voice_event_deal.c` — full handler
- `apps/earphone/key_event_deal.c` lines 318-328 — KWS event dispatch
- Config gate: `TCFG_KWS_VOICE_EVENT_HANDLE_ENABLE` (set from `TCFG_SMART_VOICE_ENABLE`)
- Board config: `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h` line 672

### What KWS Can Do (when enabled)
The KWS engine produces voice events that map to:

| KWS Event | Action |
|---|---|
| `KWS_EVENT_HEY_KEYWORD` / `KWS_EVENT_XIAOJIE` | Open voice assistant (Siri/Google) |
| `KWS_EVENT_XIAODU` | Open voice assistant |
| `KWS_EVENT_PLAY_MUSIC` | AVCTP Play |
| `KWS_EVENT_PAUSE_MUSIC` | AVCTP Pause |
| `KWS_EVENT_STOP_MUSIC` | AVCTP Stop |
| `KWS_EVENT_VOLUME_UP` | Volume up (25% step) |
| `KWS_EVENT_VOLUME_DOWN` | Volume down (25% step) |
| `KWS_EVENT_PREV_SONG` | AVCTP Prev |
| `KWS_EVENT_NEXT_SONG` | AVCTP Next |
| `KWS_EVENT_CALL_ACTIVE` | Answer call |
| `KWS_EVENT_CALL_HANGUP` | Hang up call |
| `KWS_EVENT_ANC_ON` | Enable ANC |
| `KWS_EVENT_TRANSARENT_ON` | Enable transparency mode |
| `KWS_EVENT_ANC_OFF` | Disable ANC/transparency |

### Current Status on JL7016G Hybrid
```
TCFG_SMART_VOICE_ENABLE = DISABLE_THIS_MOUDLE   ← board_jl7016g_hybrid_cfg.h line 672
TCFG_KWS_VOICE_EVENT_HANDLE_ENABLE = TCFG_SMART_VOICE_ENABLE  ← follows above → DISABLED
```

**Status: ❌ DISABLED — Code exists, compiled out. Requires external NPU or DSP wake-word engine.**

### TODO: KWS Enable Path
If wake-word detection is needed in future:
1. Set `TCFG_SMART_VOICE_ENABLE = ENABLE_THIS_MOUDLE` in board config
2. Wire compatible wake-word hardware (e.g., GX8002 NPU, AISpeech, or JL built-in KWS model)
3. Confirm mic configuration supports always-on wake detection

---

## 8. In-Ear Detection

### Architecture Overview
The in-ear (eartch) detection system has **two independent layers**:

| Layer | Macro | Purpose |
|---|---|---|
| Hardware power supply | `TCFG_EAR_DETECT_ENABLE` | Powers the external touch/capacitive/IR sensor |
| App logic handler | `TCFG_EARTCH_EVENT_HANDLE_ENABLE` | Processes wear state events and controls music/call |

These two are **independent**. The app logic can compile without the hardware layer, but it will never receive events.

---

### 8a. App Logic — `eartch_event_deal.c`

#### Code Location
- `apps/earphone/eartch_event_deal.c` — full module  
- `TCFG_EARTCH_EVENT_HANDLE_ENABLE = ENABLE_THIS_MOUDLE` — board_jl7016g_hybrid_cfg.h line 231

#### What the App Logic Does (when sensor fires events)
The `eartch_event_deal.c` module tracks two states per earbud:
- `EARTCH_STATE_IN` — earbud is in the ear
- `EARTCH_STATE_OUT` — earbud is removed

TWS state syncing: the local earbud's wear state is synced to the remote sibling using `TWS_FUNC_ID_EARTCH_SYNC` so both sides know both states.

**On Ear-IN event (earbud put back in):**
- Music was paused → resumes play (`USER_CTRL_AVCTP_OPID_PLAY`)
- Call SCO was disconnected → reconnects SCO (`USER_CTRL_CONN_SCO`)
- If A2DP link was disconnected (option) → reconnects A2DP (`USER_CTRL_CONN_A2DP`)
- TWS auto role-switch enabled: if master came back, role can switch back

**On Ear-OUT event (earbud removed):**
- Music playing → sends pause (`USER_CTRL_AVCTP_OPID_PAUSE`)
- Call active + **both** earbuds out → disconnects SCO, audio returns to phone (`USER_CTRL_DISCONN_SCO`)
- A2DP link disconnect option: if both out, disconnects A2DP link entirely (config flag `TCFG_EARTCH_MUSIC_CTL_A2DP_CONNECT = 0`, disabled by default)
- TWS role switch: if master ear is removed but slave is still in → triggers master→slave role switch

**15-second timeout behavior:**
- After both earbuds removed, `music_ctrl_en` flag can be timed out (15s). After that, putting earbuds back in will NOT auto-resume music.  
- This is controlled by `TCFG_EARTCH_MUSIC_CTL_TIMEOUT_ENABLE = 0` — **currently disabled**, so timeout is not active (music resumes any time after ear-out).

**Dynamic on/off via key:**
The feature can be toggled at runtime:
- `KEY_EARTCH_ENABLE` → saves enable flag to VM
- `KEY_EARTCH_DISABLE` → saves disable flag to VM
- Stored under `CFG_EARTCH_ENABLE_ID` (VM key 1)

#### Status: ✅ APP LOGIC COMPILED IN AND ACTIVE

---

### 8b. Hardware Power Layer — `TCFG_EAR_DETECT_ENABLE`

#### Board Config
```c
// board_jl7016g_hybrid_cfg.h line 251
#define TCFG_EAR_DETECT_ENABLE    DISABLE_THIS_MOUDLE  // external touch and in-ear detect power enable
// line 259
#define TCFG_EAR_DETECT_ENABLE    DISABLE_THIS_MOUDLE  // in-ear detect enable
```

This macro controls the power supply and GPIO routing for the external sensor. It is **disabled** on the JL7016G Hybrid config.

#### Status: ❌ HARDWARE LAYER DISABLED

This means even though the app logic (`TCFG_EARTCH_EVENT_HANDLE_ENABLE`) is compiled in and active, **it will never receive any ear-in or ear-out events** because the hardware sensor is not powered or configured.

---

## TODO List — Features Needing Investigation or Enablement

These are recorded here as tracked work items for future sessions.

---

### TODO-F001 — Wire Physical Keys to KEY_MUSIC_PP, KEY_VOL_UP/DOWN, KEY_OPEN_SIRI

**Status:** TO DO  
**Priority:** HIGH  

The key event handler code for play/pause, volume, call, and voice assistant is fully implemented. However, it only fires if a **physical key** (or touch pad) is mapped to the correct key event value in `key_table[][]`.

**What to check:**
- Find the active `key_table[][]` definition for the JL7016G board variant
- Confirm that physical keys are mapped to:
  - `KEY_MUSIC_PP`
  - `KEY_VOL_UP`
  - `KEY_VOL_DOWN`
  - `KEY_OPEN_SIRI`
  - `KEY_MUSIC_NEXT` / `KEY_MUSIC_PREV` (for skip + hangup)
- If keys are not mapped → assign them in the board key table

**Files to check:**
- `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h` — key table and key definitions
- `apps/earphone/user_cfg.c` — `key_table[][]` initialization if overridden there

---

### TODO-F002 — Verify KEY_CALL_HANG_UP and KEY_CALL_ANSWER Stubs Are Intentional

**Status:** TO DO  
**Priority:** MEDIUM  

Both `KEY_CALL_HANG_UP` and `KEY_CALL_ANSWER` cases exist in the key handler switch (`key_event_deal.c`) but their bodies are **empty**. The actual answer and hangup logic is routed through `KEY_MUSIC_PP`.

This is intentional SDK design (multi-function single key). But if your hardware has a dedicated call button, you will need to add body code to these stubs.

**Action if dedicated call button is needed:**
- Add `user_send_cmd_prepare(USER_CTRL_HFP_CALL_ANSWER, 0, NULL)` to `KEY_CALL_ANSWER` case
- Add `user_send_cmd_prepare(USER_CTRL_HFP_CALL_HANGUP, 0, NULL)` to `KEY_CALL_HANG_UP` case
- Map a physical key to `KEY_CALL_HANG_UP` / `KEY_CALL_ANSWER` in the key table

---

### TODO-F003 — Enable In-Ear Detection Hardware (`TCFG_EAR_DETECT_ENABLE`)

**Status:** TO DO  
**Priority:** MEDIUM (if in-ear detect feature is wanted in production)  

The app logic for in-ear detection is **compiled in and working** (`TCFG_EARTCH_EVENT_HANDLE_ENABLE = ENABLE`). The hardware layer is **disabled** (`TCFG_EAR_DETECT_ENABLE = DISABLE`).

**What is needed to activate full in-ear detection:**
1. Identify what sensor is mounted on the JL7016G Hybrid PCB (capacitive touch, IR proximity, optical, etc.)
2. Determine the correct GPIO and power supply line for the sensor
3. Set `TCFG_EAR_DETECT_ENABLE = ENABLE_THIS_MOUDLE` in `board_jl7016g_hybrid_cfg.h`
4. Configure any sensor-specific GPIO (check for `TCFG_EAR_DETECT_PORT` or similar macro in board config)
5. Test both earbuds: remove one → music should pause; replace it → music should resume

**Risk:** Enabling the hardware power layer without confirming the correct GPIO could conflict with other peripheral GPIO assignments. Do not enable blindly — verify PCB schematic first.

---

### TODO-F004 — Evaluate Wake-Word KWS Voice Assistant for Production

**Status:** TO DO  
**Priority:** LOW (advanced feature)  

The KWS (Keyword Spotting) voice assistant engine is completely implemented in code but disabled on this board (`TCFG_SMART_VOICE_ENABLE = DISABLE`).

**What KWS enables:**
- Hands-free wake word (e.g., "Hey Siri", "小节", "小度")
- Voice-controlled play/pause, volume, next/prev, answer/hangup, ANC mode changes

**What is needed to enable KWS:**
1. Confirm a compatible always-on mic input chain is available on the PCB
2. Select a KWS engine — options seen in the SDK:
   - JL built-in KWS model (`apps/common/jl_kws/`)
   - GX8002 external NPU (`apps/common/device/gx8002_npu/`)
   - AISpeech DSP (`cpu/br28/smart_voice/aispeech_asr.c`)
3. Set `TCFG_SMART_VOICE_ENABLE = ENABLE_THIS_MOUDLE`
4. Configure the specific KWS backend macro
5. Verify MIC chain is compatible with always-on low-power wake mode

**Note:** Enabling KWS may increase idle power consumption significantly. Evaluate against battery life budget before enabling.

---

## Key Macro Reference

| Macro | File | Line | Value | Meaning |
|---|---|---|---|---|
| `TCFG_EARTCH_EVENT_HANDLE_ENABLE` | `board_jl7016g_hybrid_cfg.h` | 231 | `ENABLE_THIS_MOUDLE` | In-ear app logic compiled and active |
| `TCFG_EAR_DETECT_ENABLE` | `board_jl7016g_hybrid_cfg.h` | 251, 259 | `DISABLE_THIS_MOUDLE` | Hardware sensor power — OFF |
| `TCFG_SMART_VOICE_ENABLE` | `board_jl7016g_hybrid_cfg.h` | 672 | `DISABLE_THIS_MOUDLE` | KWS wake-word engine — OFF |
| `TCFG_KWS_VOICE_EVENT_HANDLE_ENABLE` | `board_jl7016g_hybrid_cfg.h` | 673, 701 | follows `TCFG_SMART_VOICE_ENABLE` | KWS event handler — OFF |
| `TCFG_CALL_KWS_SWITCH_ENABLE` | `board_jl7016g_hybrid_cfg.h` | 682 | follows `TCFG_SMART_VOICE_ENABLE` | KWS in-call switch — OFF |
| `TCFG_EARTCH_MUSIC_CTL_TIMEOUT_ENABLE` | `eartch_event_deal.c` | 51 | `0` | 15s music ctrl timeout — disabled |
| `TCFG_EARTCH_CALL_CTL_SCO_CONNECT` | `eartch_event_deal.c` | 53 | `1` | SCO disconnect on ear-out — active |
| `TCFG_EARTCH_AUTO_CHANGE_MASTER` | `eartch_event_deal.c` | 54 | `1` | Auto role-switch on ear-out — active |
| `TCFG_EARTCH_SWITCH_CFG_ENABLE` | `eartch_event_deal.c` | 55 | `1` | Runtime enable/disable toggle — active |

---

## Source File Reference

| File | Relevance |
|---|---|
| `apps/earphone/key_event_deal.c` | All key-to-action mappings: play/pause, vol, call, Siri |
| `apps/earphone/eartch_event_deal.c` | Full in-ear detection app logic |
| `apps/earphone/kws_voice_event_deal.c` | KWS wake-word event handler |
| `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h` | All config gates: EAR_DETECT, KWS, EARTCH |
| `apps/earphone/include/app_config.h` | TWS, key mode config |
| `include_lib/btstack/avctp_user.h` | All `USER_CTRL_*` command enum definitions |

---

## Related FIX Records

| Fix | Title | Relevance |
|-----|-------|-----------|
| [FIX-020](../../FIXING/FIX-020%20—%20TWS%20Volume%20Desync%20Between%20Buds.md) | TWS volume desync | Volume sync API (`tws_api_send_data_to_sibling`) |
| [FIX-021](../../FIXING/FIX-021%20—%20Per-Bud%20Key%20Table%20Split%20Does%20Not%20Work%20in%20TWS.md) | Compile-time key splits ineffective | Volume/key dispatch architecture |
| [FIX-022](../../FIXING/FIX-022%20—%20Right%20Bud%20Vol%20Up%20Left%20Bud%20Vol%20Down%20Channel-Aware%20Dispatch.md) | Per-bud channel-aware dispatch | Full volume / playback control implementation |
