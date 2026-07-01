# Updated Log 3 - MAC Verified + ADV/Volume Behavior

## Scope

This document analyzes your newest log dump (the one ending with `àÿ`) and answers:
- Is manual MAC provisioning now working?
- Why are BLE advertising toggles repeating?
- Why is `set_vol[music]` moving continuously?
- Which lines are faults vs normal runtime behavior?

## Final Verdict

## 1) Manual MAC provisioning status

**Working now.**

Evidence in this log:
- `[USER_CFG]Provisioning Pair 1 - RIGHT BUD (B02)` appears.
- Written values are correct:
  - `CFG_BT_MAC_ADDR (102) = 3C:00:0A:7E:1A:01`
  - `CFG_TWS_LOCAL_ADDR (95) = 3C:00:0A:7E:1A:01`
  - `CFG_TWS_REMOTE_ADDR (96) = 3C:00:0A:7E:1A:00`
  - `CFG_TWS_COMMON_ADDR (97) = AA:BB:CC:00:01:FF`
  - `CFG_TWS_CHANNEL (98) = 0x01 [RIGHT]`
  - `CFG_TWS_PAIR_CODE_ID (602) = 0x6688`
- Runtime address banner confirms EDR is now correct:
  - `-----edr + ble 's address-----`
  - `3C 00 0A 7E 1A 01` (EDR)

Conclusion: the previous mismatch (`BB 0A ...` appearing as local EDR) is resolved in this capture.

## 2) TWS relationship status

**Working, but not fully seamless yet.**

Evidence:
- `tws_task_init` shows local `3C 00 0A 7E 1A 01`.
- Page/link lines show local and sibling pair:
  - local `3C ... 01`
  - sibling `3C ... 00`
- TWS mode transitions and sync events occur (`event=2`, mode change, monitor setup).

Project note:
- Seamlessness is still under improvement (adv churn/retry windows still visible).
- PC5 pull bias remains a required hardware condition for this project.

## 3) Phone connection behavior

**Working with transient retries/noise.**

Evidence:
- HCI/LMP stack comes up and completes SSP/encryption sequence.
- `BT_STATUS_CONNECTED` and `BT_STATUS_FIRST_CONNECTED` occur.
- HFP AT command sequence appears (`AT+BRSF`, `AT+BAC`, `AT+CIND`, `AT+CMER`, `AT+CHLD`, `AT+CMEE`).
- A2DP media starts (`BT_STATUS_A2DP_MEDIA_START`, `a2dp_media_type:AAC`).

## Chronological explanation by log phases

## Phase A: Clock/Reset/RTOS startup (0.100s)

Lines:
- `[CLOCK]...` register dump
- reset chain (`MSYS_P11_RST`, `P11_P33_RST`, `P33_VDDIO_POR_RST`)
- task creation (`systimer`, `app_core`, `idle0/1`, `sys_event`)

Meaning:
- normal cold boot sequence; no failure signature.

## Phase B: VM and board init (0.127s onward)

Lines:
- VM mount and capacity
- board power init
- P33 wakeup/mux register dump
- ADC rail readings (`vbat`, `dtemp`, `hpvdd`)

Meaning:
- storage and power domains initialized correctly.

## Phase C: USER_CFG load + manual provisioning hook

Important ordering:
- `tws pair code config: FF FF` appears first (pre-existing read before hook write).
- provisioning function writes correct pair values after that.

This ordering is expected due to current function flow and does not mean provisioning failed.

## Phase D: Runtime identity print

Lines:
- `[USER_CFG]mac:` shows `3C 00 0A 7E 1A 01`
- banner `edr + ble's address` shows:
  - EDR: `3C 00 0A 7E 1A 01`
  - BLE: `4C 00 0A 23 1F 12`

Meaning:
- runtime identity is consistent with manual right-bud config.

## Phase E: BT/TWS bring-up and role changes

Lines:
- `tws_connection_start`, `pend_in`, `accepted_switch_req`, `pend_exit`
- repeated `tws-user` events with reason/event codes
- sniff/unsniff periodic lines (`state:1` with r/m/l counters)

Meaning:
- normal TWS power-management and role-sync behavior.
- repeated periodic lines are expected telemetry, not errors.

## Phase F: Advertising state churn

Lines:
- `adv modify!!!!!!`
- `set_adv_enable 0` / `set_adv_enable 1`
- `ble_work_st:20->2` and `2->20`
- occasional `LL Adv already destroy`

Meaning:
- RCSP/TWS state machine is toggling BLE advertising in response to role/connection updates.
- `LL Adv already destroy` here is usually a race/informational warning (disable called while already disabled).

## Phase G: `config.dat` missing

Lines:
- `[SDFILE]Open ... [/config.dat] Fail! (>_<)`
- `file open fail`

Meaning:
- optional file not present in your filesystem package.
- not blocking BT/TWS/A2DP core operation.

## Phase H: Audio prompts and decoder warnings

Lines:
- tone start/stop lines (`power_on.wts`, `bt_conn.wts`, sine tones)
- `wtgv2_dec err:64` appears.

Meaning:
- prompt decoder warning occurs, but stream/system recovery is normal.
- non-fatal in this trace.

## Phase I: A2DP media and volume changes

Lines:
- `BT_STATUS_A2DP_MEDIA_START`
- `a2dp_media_type:AAC`
- many `set_vol[music]:music=x` changes (4..16 etc)

Meaning:
- volume is being synchronized dynamically (phone AVRCP absolute volume / TWS sync / profile transitions).
- this fluctuation pattern is normal during connect and mode-change windows unless user hears unstable loudness constantly.

## Why `set_vol[music]` moves so much

Likely combined sources:
1. phone absolute volume sync events
2. TWS peer volume sync
3. prompt playback ducking/recovery transitions
4. state switches between tone/music/idle

If audible pumping is a user issue, add rate-limit/debounce in volume sync path; otherwise this is expected debug chatter.

## Why BB:0A:2C:77:5B:37 still appears in some lines

In this log, `BB 0A 2C 77 5B 37` appears during some connection attempts/telemetry blocks.
Interpretation:
- those blocks can include remote/peer or cached transport fields, not necessarily your local runtime EDR identity.
- local identity is validated by `[USER_CFG]mac` and `edr+ble` banner showing `3C ... 01`.

## Fault classification for this log

## Critical
- None observed for boot/connect path.

## Medium
- repeated `config.dat` open fail (feature-dependent, can be cleaned by packaging file)
- occasional adv state race warning (`LL Adv already destroy`)

## Low
- `wtgv2_dec err:64` prompt decode warning
- repeated debug noise bursts (`PPP`, `uuu`, `C`, `s`, `w`, `àÿ`) from mixed UART stream

## Acceptance checklist (this log)

- Manual provisioning banner present: PASS
- Correct right-bud syscfg values written: PASS
- Runtime local EDR address equals manual target: PASS
- TWS sibling mapping reciprocal behavior visible: PASS
- TWS + phone + A2DP flow completes: PASS

Overall: **implementation is now behaving correctly for right-bud profile in this capture.**
