# JL7016G SDK — End-to-End Fix & Progress Tracker
**Chip:** AC701N (BR28 core)  **Board:** JL7016G Hybrid — ANC TWS Earphone  
**Goal:** Clean, buildable, fully-functional TWS Earphone firmware  
**SDK Base:** FIRST PERIORITY SDK  

---

## Fix Status Overview

| #   | Issue                                                                                                                                                                                       | File                                                                                      | Status     | Doc Link                                                                     |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------- |
| 001 | `TCFG_IMU_SENSOR_PWR_PORT` undeclared identifier — build error                                                                                                                              | `board_jl7016g_hybrid_cfg.h`                                                              | ✅ FIXED    | [[FIXING/FIX-001 — TCFG_IMU_SENSOR_PWR_PORT Undeclared]]                     |
| 002 | `lis2dh12_driver.o` missing at link (filename mismatch)                                                                                                                                     | `AC701N.cbp`, `sdk.elf.objs.txt`                                                          | ✅ FIXED    | [[FIXING/FIX-002 — lis2de12 driver object missing at link]]                  |
| 003 | undefined refs: `app_online_db_*`, `pca_open`, `a2dp_opened`                                                                                                                                | `AC701N.cbp`, `online_db_deal.c`, `sdk.elf.objs.txt`                                      | ✅ FIXED    | [[FIXING/FIX-003 — undefined references online_db and fft_pca symbols]]      |
| 004 | TWS not forming with same firmware until L/R hardware split verified                                                                                                                        | `app_config.h`, `bt_tws.c`, board hardware `PC5`                                          | ✅ VERIFIED | [[FIXING/FIX-004 — TWS auto pairing and PC5 channel select validation]]      |
| 005 | BLE MAC set in Config GUI never applied — always derived from EDR MAC                                                                                                                       | `apps/earphone/earphone.c`                                                                | ✅ FIXED    | [[FIXING/FIX-005 — BLE MAC Address Ignored at Boot]]                         |
| 006 | Hardcoded `bt_modify_name("Buddie")` overwrites Config GUI name every boot                                                                                                                  | `apps/earphone/app_main.c`                                                                | ✅ FIXED    | [[FIXING/FIX-006 — Hardcoded Buddie Name Overwrites Config GUI Name]]        |
| 007 | PB4 gestures detected in LP logs but no app action (events dropped on eartch reference channel)                                                                                             | `cpu/br28/lp_touch_key.c`, `board_jl7016g_hybrid_cfg.h`                                   | ✅ FIXED    | [[FIXING/FIX-007 — PB4 gestures dropped on eartch reference channel]]        |
| 008 | CH3 long/hold valid touches suppressed by long-by-res gate (`diff < cfg2/2`)                                                                                                                | `cpu/br28/lp_touch_key.c`, `board_jl7016g_hybrid_cfg.h`                                   | ✅ FIXED    | [[FIXING/FIX-008 — CH3 long hold suppressed by long-by-res gate]]            |
| 009 | PB4 valid touch ranges flagged invalid by low algo range ceiling                                                                                                                            | `cpu/br28/lp_touch_key.c`, `board_jl7016g_hybrid_cfg.h`                                   | ✅ FIXED    | [[FIXING/FIX-009 — PB4 touch range rejected by low algorithm max]]           |
| 010 | In-ear remap hook could still compile/intercept LP keys when ear-detect disabled                                                                                                            | `apps/common/device/in_ear_detect/in_ear_detect.c`                                        | ✅ FIXED    | [[FIXING/FIX-010 — in-ear remap hook active while ear detect disabled]]      |
| 011 | UART debug stream partially garbled during bring-up due terminal framing/config                                                                                                             | board UART config + host terminal setup                                                   | ✅ FIXED    | [[FIXING/FIX-011 — UART framing mismatch during touch bring-up]]             |
| 012 | MIC produces zero audio — `TCFG_AUDIO_MIC_PWR_CTL = MIC_PWR_FROM_MIC_LDO` routes power to PA0 which is not connected in schematic                                                           | `board_jl7016g_hybrid_cfg.h`                                                              | ✅ FIXED    | [[FIXING/FIX-012 — MIC power PA0 unconnected switched to PA2 MICBIAS]]       |
| 013 | MIC picks up only direct taps, not speech — `TCFG_AUDIO_MIC_MODE = AUDIO_MIC_CAP_DIFF_MODE` but MIC0 is single-ended on PA1                                                                 | `board_jl7016g_hybrid_cfg.h`                                                              | ✅ FIXED    | [[FIXING/FIX-013 — MIC0 differential mode mismatch changed to single-ended]] |
| 014 | Maximum playback volume too low on JL7016G Hybrid because ANC digital ceiling was effectively capped at `-17 dB`; raised board-specific ceiling to `-6 dB`                                  | `cpu/br28/audio_config.h`                                                                 | ✅ FIXED    | [[BOARD — JL7016G Hybrid Config Deep Study]]                                 |
| 015 | PB1 (CH1) completely silent — event dispatcher blocked CH1 unconditionally, LONG press handler blocked CH1, thresholds reversed (inear/outear swapped), sensitivity table mismatched vs PB4 | `cpu/br28/lp_touch_key.c`, `board_jl7016g_hybrid_cfg.h`, `apps/earphone/key_event_deal.c` | ✅ FIXED    | [[FIXING/FIX-015 — PB1_COMPLETE_SOLUTION]]                                   |
| 016 | CH1 three silent blockers (EARTCH hw mode bit, missing `TouchAlgo_Init`, RAISING intercept) + PC3 GPIO output feature added (polarity later inverted by FIX-019) | `cpu/br28/lp_touch_key.c`, `board_jl7016g_hybrid_cfg.h` | ✅ FIXED | [[FIXING/FIX-016 — PB1 PC3 GPIO Touch Feedback]] |
| 017 | Holding PB1 triggered soft power-off — `ch[1].key_value = 0` mapped HOLD to `KEY_POWEROFF_HOLD`; changed to `key_value = 2` (same row as PB4, HOLD = `KEY_VOL_UP`) | `apps/earphone/board/br28/board_jl7016g_hybrid.c` | ✅ FIXED | [[FIXING/FIX-017 — PB1 Hold Power-Off Fix]] |
| 018 | PB1 touch was dispatching SHORT/LONG/HOLD key events (play/pause, next, vol) — `__ctmu_notify_key_event()` had no CH1 guard; added `TCFG_LP_TOUCH_PB1_LED_FEEDBACK_ENABLE` guard to suppress all PB1 app events; PB1 is now GPIO-only, PB4 handles all controls | `cpu/br28/lp_touch_key.c` | ✅ FIXED | [[FIXING/FIX-018 — PB1 Key Events Suppressed GPIO Only]] |
| 019 | PC3 GPIO output polarity inverted from active-HIGH to active-LOW — idle=HIGH, touch=LOW, release=HIGH; swapped `ACTIVE_LEVEL` ↔ `!ACTIVE_LEVEL` in FALLING handler, RAISING handler, and init gpio_write | `cpu/br28/lp_touch_key.c` | ✅ FIXED | [[FIXING/FIX-019 — PC3 Polarity Inverted (Active LOW)]] |
| 020 | TWS volume desync — slave bud changed its own DAC but master never received the new level; `bt_tws_sync_volume()` used `tws_api_send_data_to_slave` (master→slave only); changed to `tws_api_send_data_to_sibling` (bidirectional) | `apps/earphone/bt_tws.c` | ✅ FIXED | [[FIXING/FIX-020 — TWS Volume Desync Between Buds]] |
| 021 | `#if TCFG_RIGHT_BUD` key-table split had no effect in TWS — master always evaluates its own table for all events including forwarded slave touches; compile-time per-bud key-table splits are ineffective | `apps/earphone/board/br28/board_jl7016g_hybrid.c` | ✅ FIXED | [[FIXING/FIX-021 — Per-Bud Key Table Split Does Not Work in TWS]] |
| 022 | Right bud HOLD=VolUp / Left bud HOLD=VolDown using runtime channel detection via `key_tws_lr_diff_deal()` + `lr_diff_otp_deal()`; also Right=Next / Left=Prev on double-tap; single firmware for both buds | `apps/earphone/key_event_deal.c`, `board_jl7016g_hybrid.c` | ✅ FIXED | [[FIXING/FIX-022 — Right Bud Vol Up Left Bud Vol Down Channel-Aware Dispatch]] |

---

## Folders

| Folder    | Purpose                                                           |
| --------- | ----------------------------------------------------------------- |
| `FIXING/` | One note per bug fix — root cause + change made + verification    |
| `UPDATE/` | SDK library/tool version update notes                             |
| `BOARD/`  | *(to be created)* Board pinout, enabled features, full config map |
| `AUDIO/`  | *(to be created)* ANC, CVP, EQ, DAC/MIC chain details             |
| `BT/`     | *(to be created)* Bluetooth TWS, BLE, profiles config             |
| `BUILD/`  | *(to be created)* Build system, Makefile, toolchain notes         |

---

## Feature Audits & Deep Dives

| Doc                                                                                             | Scope                                                                                                                                                                                                                                                                                                                                                       | Date       |
| ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| [[FEATURE AUDIT — Playback Controls, Call Controls, Volume, Voice Assistant, In-Ear Detection]] | Key controls, Siri/Google, KWS, in-ear detect                                                                                                                                                                                                                                                                                                               | 2026-04-22 |
| [[AUDIO DEEP DIVE — TWS Streaming, Sync, Reconnection Delays & Glitches]]                       | TWS seamless audio, sync mechanism, reconnect timing, glitch root causes                                                                                                                                                                                                                                                                                    | 2026-04-23 |
| [[AUDIO CODEC QUALITY — Supported Codecs, Bitrates & Configuration]]                            | SBC/AAC/LDAC/aptX/mSBC/CVSD/LC3 codecs, bitrates, quality ratings, enable options                                                                                                                                                                                                                                                                           | 2026-04-23 |
| [[CONFIG GUI DEEP DIVE — AC701N Config Tool Online Offline Workflow]]                           | GUI config architecture: jlxproj tools, cfg/eq/anc bin generation, online SPP/USB/UART update path, packaging behavior                                                                                                                                                                                                                                      | 2026-04-23 |
| [[CONFIG GUI FIELD REFERENCE — Every Tab Every Option Explained]]                               | All 8 tabs: BT Config (names/MAC/power/BLE), Common Config (events/LED/tone/charge), Call Config (CVP AEC/NS/AGC/NLP params), Microphone Config (mode/bias/LDO), Tone File Config (.wts assignments), Volume Config (MeanStep/FixedStep tables), ANC Config (gains/DRC/topology), Device Info — with actual project values from cfg_tool_state_complete.lua | 2026-04-24 |

---

## Active Board Configuration

- **Config macro:** `CONFIG_BOARD_JL7016G_HYBRID`  
- **Config file:** `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h`  
- **Global build cfg:** `apps/earphone/board/br28/board_jl7016g_hybrid_global_build_cfg.h`  
- **Board variant in use:** `EARPHONE_HYBRID` (CLIENT_BOARD == 0x02)  

---

## Build Command

```bat
.vscode/winmk.bat all
```
Build output: `obj/Release/`

---

## Next Priority Fixes

- [x] Verify full clean build passes with FIX-001, FIX-002, and FIX-003 applied  
- [x] Verify real-board TWS bring-up with hardware L/R split on `PC5` (one pull-down, one pull-up)  
- [x] Feature audit: play/pause, call, volume, voice assistant, in-ear detection — documented  
- [x] TODO-F001: Verify physical keys are mapped to `KEY_MUSIC_PP`, `KEY_VOL_UP/DOWN`, `KEY_OPEN_SIRI` in key_table  
- [x] TODO-F002: Decide if dedicated call button stubs (`KEY_CALL_HANG_UP`, `KEY_CALL_ANSWER`) need body code  
- [x] TODO-F003: Enable in-ear detection hardware (`TCFG_EAR_DETECT_ENABLE`) — requires PCB schematic review first  
- [ ] TODO-F004: Evaluate KWS wake-word voice assistant for production — requires mic chain + power budget review  
- [x] PB4 touch routing fix chain documented (range, long/hold gate, remap gate, ref-channel passthrough)
- [x] UART debug workflow and framing fix documented (`115200 8N1`, no flow control)
- [x] Main MIC power path corrected: PA0 MICLDO -> PA2 MICBIAS (FIX-012)
- [x] Main MIC0 capture mode corrected: differential -> single-ended (FIX-013)
- [x] Max playback/output ceiling increased for JL7016G Hybrid ANC path (`DIG_VOL_MAX_VALUE: -17 dB -> -6 dB`)
- [x] PB1 (CH1) fully unblocked: event dispatcher, LONG press handler, thresholds corrected, sensitivity matched to PB4 (FIX-015)
- [x] CH1 three blocking points resolved (EARTCH hw mode, TouchAlgo_Init, RAISING intercept); PC3 GPIO output mirrors PB1 touch state in real time (FIX-016)
- [x] PB1 HOLD no longer powers off device — `ch[1].key_value` changed from 0 to 2 (FIX-017)
- [x] PB1 (CH1) key events suppressed — PB1 is GPIO-only (PC3 toggle), all music/volume control stays on PB4 (CH3) (FIX-018)
- [x] PC3 polarity inverted to active-LOW — idle HIGH, touch LOW, release HIGH (FIX-019)
- [x] TWS volume desync fixed — `bt_tws_sync_volume()` changed to `tws_api_send_data_to_sibling` (bidirectional) (FIX-020)
- [x] Discovered: `#if TCFG_RIGHT_BUD` key-table compile-time splits are ineffective in TWS — master owns all event dispatch (FIX-021)
- [x] Right bud HOLD=VolUp / Left bud HOLD=VolDown — runtime channel detection via `key_tws_lr_diff_deal()` in `KEY_VOL_UP` and `KEY_MUSIC_NEXT` handlers; single firmware for both buds (FIX-022)
- [ ] Audit any other board-specific macros missing from JL7016G config  
- [ ] Audit gSensor/IMU driver naming consistency across IDE/build metadata  
- [ ] Review non-blocking linker stack-size warnings and optimize top offenders  
- [ ] Validate ANC parameters and mic configuration for TWS  
- [ ] Review power management settings for production  
