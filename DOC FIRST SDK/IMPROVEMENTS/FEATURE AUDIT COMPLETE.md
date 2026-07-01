---
tags: [audit, features, enabled, disabled, tcfg, config, jl7016g, reference]
date: 2026-06-08
status: COMPLETE — REFERENCE ONLY
effort: N/A
---

# 📋 Feature Audit Complete — JL7016G Hybrid SDK

> Ground-truth reference for all `TCFG_*` and `CONFIG_*` flags across the active build configuration.
> Source files: `board_jl7016g_hybrid_cfg.h`, `board_jl7016g_hybrid_global_build_cfg.h`, `audio_config.h`, `user_cfg.c`
> Last audited: 2026-06-08 against SDK version JL701N_V1.6.1

---

## Quick Navigation

- [→ IMPROVEMENTS/README.md](./README.md) — Priority matrix and all improvement links
- [→ AUDIO IMPROVEMENTS/](./AUDIO%20IMPROVEMENTS/README.md)
- [→ CONNECTION IMPROVEMENTS/](./CONNECTION%20IMPROVEMENTS/README.md)
- [→ Existing Feature Audit](../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/FEATURE%20AUDIT.md)

---

## Section 1 — Audio Features ENABLED ✅

| Flag / Setting                | Value                     | File               | Notes                               |
| ----------------------------- | ------------------------- | ------------------ | ----------------------------------- |
| `CONFIG_ANC_ENABLE`           | `1`                       | global_build_cfg.h | Hybrid ANC active                   |
| `TCFG_AUDIO_ANC_ENABLE`       | `CONFIG_ANC_ENABLE`       | board_cfg.h        | Tied to global flag                 |
| `ANC_TRAIN_MODE`              | `ANC_HYBRID_EN`           | board_cfg.h        | FF + FB hybrid                      |
| `ANC_CH`                      | `ANC_L_CH`                | board_cfg.h        | Left channel only                   |
| `ANCL_FF_MIC`                 | `A_MIC1`                  | board_cfg.h        | Feedforward mic = MIC1 (PA4)        |
| `ANCL_FB_MIC`                 | `A_MIC2`                  | board_cfg.h        | Feedback/error mic = MIC2 (PG7)     |
| `TCFG_AUDIO_ADC_ENABLE`       | `ENABLE`                  | board_cfg.h        | ADC/microphone input on             |
| `TCFG_AUDIO_DAC_ENABLE`       | `ENABLE`                  | board_cfg.h        | DAC/speaker output on               |
| `TCFG_AUDIO_HPVDD_ENABLE`     | `ENABLE`                  | board_cfg.h        | 1.85V external DAC power (PG6)      |
| `TCFG_AUDIO_DAC_CONNECT_MODE` | `DAC_OUTPUT_MONO_L`       | board_cfg.h        | Mono left channel output            |
| `TCFG_AUDIO_DAC_MODE`         | `DAC_MODE_L_DIFF`         | board_cfg.h        | Low-voltage differential (earphone) |
| `TCFG_EQ_ENABLE`              | `1`                       | board_cfg.h        | 10-band EQ                          |
| `TCFG_BT_MUSIC_EQ_ENABLE`     | `1`                       | board_cfg.h        | Music EQ                            |
| `TCFG_PHONE_EQ_ENABLE`        | `1`                       | board_cfg.h        | Call path EQ                        |
| `TCFG_DYNAMIC_ADC_GAIN`       | `ENABLE`                  | board_cfg.h        | Switches gain between ANC/call mode |
| `SYS_VOL_TYPE`                | `VOL_TYPE_DIGITAL_HW`     | audio_config.h     | Hardware digital volume control     |
| `SYS_MAX_VOL`                 | `MAX_DIG_VOL` (16 levels) | audio_config.h     | 16 volume steps                     |
| `DIG_VOL_MAX_VALUE`           | `-6.0 dB`                 | audio_config.h     | Cap enforced due to ANC             |
| `DIG_VOL_STEP`                | `-3.0 dB` per step        | audio_config.h     | Each step = 3dB                     |
| `MAX_ANA_VOL`                 | `3` (0–3)                 | audio_config.h     | Analog volume range                 |
| `TCFG_AUDIO_ADC_MIC_CHA`      | `AUDIO_ADC_MIC_0`         | board_cfg.h        | Primary call mic = MIC0 (PA1)       |
| `TCFG_AUDIO_MIC_MODE`         | `AUDIO_MIC_CAP_MODE`      | board_cfg.h        | Single-ended capacitive coupling    |
| `TCFG_AUDIO_MIC1_MODE`        | `AUDIO_MIC_CAP_DIFF_MODE` | board_cfg.h        | Differential — ANC FF mic           |
| `TCFG_AUDIO_MIC2_MODE`        | `AUDIO_MIC_CAP_DIFF_MODE` | board_cfg.h        | Differential — ANC FB mic           |
| `TCFG_AUDIO_MIC_PWR_CTL`      | `MIC_PWR_FROM_MIC_BIAS`   | board_cfg.h        | Internal MICBIAS LDO                |
| `TCFG_DEC_WTGV2_ENABLE`       | `ENABLE`                  | board_cfg.h        | Proprietary tone format             |
| `TCFG_DEC_SBC_ENABLE`         | `ENABLE`                  | board_cfg.h        | SBC Bluetooth audio                 |
| `TCFG_ENC_MSBC_ENABLE`        | `ENABLE`                  | board_cfg.h        | mSBC wide-band call                 |
| `TCFG_ENC_CVSD_ENABLE`        | `ENABLE`                  | board_cfg.h        | CVSD narrow-band call               |
| `TCFG_ENC_OPUS_ENABLE`        | `ENABLE`                  | board_cfg.h        | OPUS encode (TWS link)              |
| `TCFG_BT_SUPPORT_AAC`         | `1`                       | board_cfg.h        | AAC audio codec                     |
| `TCFG_BT_SUPPORT_LDAC`        | `1`                       | board_cfg.h        | LDAC hi-res audio                   |
| `TCFG_WTG_TONE_MIX_ENABLE`    | `ENABLE`                  | board_cfg.h        | WTG tone overlay                    |
| `TCFG_WTS_TONE_MIX_ENABLE`    | `ENABLE`                  | board_cfg.h        | WTS tone overlay                    |
| CVP mode                      | `CVP_DNS_MODE`            | user_cfg.c         | Deep Neural Network denoiser        |

---

## Section 2 — Audio Features DISABLED ⛔ (Improvement Candidates)

| Flag / Setting | Value | File | Improvement Doc |
|---|---|---|---|
| `TCFG_DRC_ENABLE` | `0` | board_cfg.h | [AUDIO-IMP-001](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-001%20—%20DRC%20Dynamic%20Range%20Compression.md) |
| `TCFG_BT_MUSIC_DRC_ENABLE` | `0` | board_cfg.h | [AUDIO-IMP-001](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-001%20—%20DRC%20Dynamic%20Range%20Compression.md) |
| `TCFG_AUDIO_DUAL_MIC_ENABLE` | `DISABLE` | board_cfg.h | [AUDIO-IMP-002](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-002%20—%20Dual-Mic%20ENC%20Call%20Quality.md) |
| `ANCR_FF_MIC` | `MIC_NULL` | board_cfg.h | [AUDIO-IMP-003](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-003%20—%20ANC%20Right%20Channel%20Extension.md) |
| `ANCR_FB_MIC` | `MIC_NULL` | board_cfg.h | [AUDIO-IMP-003](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-003%20—%20ANC%20Right%20Channel%20Extension.md) |
| `TCFG_AUDIO_ANC_WIND_NOISE_DET_ENABLE` | `DISABLE` | board_cfg.h | [AUDIO-IMP-004](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-004%20—%20Wind%20Noise%20Detection.md) |
| `TCFG_AUDIO_SPEAK_TO_CHAT_ENABLE` | `DISABLE` | board_cfg.h | [AUDIO-IMP-005](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-005%20—%20Speak-to-Chat%20Transparency%20Mode.md) |
| `TCFG_AUDIO_ANC_EAR_ADAPTIVE_EN` | `DISABLE` | board_cfg.h | [AUDIO-IMP-006](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-006%20—%20Adaptive%20ANC%20Ear-Canal%20Fit.md) |
| `TCFG_DEC_LC3_ENABLE` | `DISABLE` | board_cfg.h | [AUDIO-IMP-007](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-007%20—%20LC3%20Codec%20LE%20Audio.md) |
| `DIG_VOL_MAX_VALUE` | `-6.0 dB` (capped) | audio_config.h | [AUDIO-IMP-010](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-010%20—%20Volume%20Ceiling%20and%20ANC%20Cap%20Analysis.md) |
| `TCFG_ANC_TOOL_DEBUG_ONLINE` | `DISABLE` | board_cfg.h | [AUDIO-IMP-008](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-008%20—%20EQ%20Profile%20Reference%20and%20Tuning.md) |
| `TCFG_WAV_TONE_MIX_ENABLE` | `DISABLE` | board_cfg.h | Low priority — WTG covers tones |
| `TCFG_MP3_TONE_MIX_ENABLE` | `DISABLE` | board_cfg.h | Low priority |
| MIC0 call gain (`talk_mic_gain`) | `13 dB` | user_cfg.c | [AUDIO-IMP-009](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-009%20—%20MIC%20Gain%20Optimization.md) |
| ANC-FF gain (`ff_mic_gain`) | `13 dB` | user_cfg.c | [AUDIO-IMP-009](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-009%20—%20MIC%20Gain%20Optimization.md) |
| ANC-FB gain (`fb_mic_gain`) | `0 dB` | user_cfg.c | [AUDIO-IMP-009](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-009%20—%20MIC%20Gain%20Optimization.md) |
| EQ profile (reference tones) | none documented | — | [AUDIO-IMP-008](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-008%20—%20EQ%20Profile%20Reference%20and%20Tuning.md) |

---

## Section 3 — Audio Features DISABLED ⛔ (Out of Scope / Hardware Constraint)

| Flag / Setting | Value | Reason Excluded |
|---|---|---|
| `TCFG_SMART_VOICE_ENABLE` | `DISABLE` | Requires external KWS chip or large flash model |
| `TCFG_AUDIO_HEARING_AID_ENABLE` | `DISABLE` | Regulatory / target product mismatch |
| `TCFG_AUDIO_TRIPLE_MIC_ENABLE` | `DISABLE` | No 3rd mic on PCB |
| `TCFG_CVP_DEVELOP_ENABLE` | `DISABLE` | Requires custom DSP algorithm |
| `TCFG_AUDIO_OUTPUT_IIS` | `DISABLE` | No I2S DAC on board |
| `TCFG_AUDIO_INPUT_IIS` | `DISABLE` | No I2S ADC on board |
| `TCFG_DEC_MP3_ENABLE` | `DISABLE` | No local storage playback path in this build |
| `TCFG_DEC_WAV_ENABLE` | `DISABLE` | Same |
| `TCFG_DEC_FLAC_ENABLE` | `DISABLE` | Same |
| `TCFG_DEC_APE_ENABLE` | `DISABLE` | Same — APE too CPU-heavy |
| `TCFG_DEC_AMR_ENABLE` | `DISABLE` | Voice recorder not in product scope |
| `TCFG_AEC_TOOL_ONLINE_ENABLE` | `DISABLE` | Dev/tuning tool — not needed in production |
| `TCFG_AUDIO_CVP_DUT_ENABLE` | `DISABLE` | Production test mode |
| `TCFG_AUDIO_DATA_EXPORT_ENABLE` | `DISABLE` | Debug audio export — production off |

---

## Section 4 — Connection / BT Features ENABLED ✅

| Flag / Setting | Value | File | Notes |
|---|---|---|---|
| `TCFG_USER_TWS_ENABLE` | `1` | board_cfg.h | TWS enabled |
| `CONFIG_TWS_PAIR_MODE` | `CONFIG_TWS_PAIR_BY_AUTO` | board_cfg.h | Auto-pair on boot |
| `CONFIG_TWS_CHANNEL_SELECT` | `CONFIG_TWS_EXTERN_DOWN_AS_LEFT` | board_cfg.h | PC5 pull-down = left bud |
| `CONFIG_TWS_CONNECT_SIBLING_TIMEOUT` | `4` seconds | board_cfg.h | Sibling connect window |
| `CONFIG_TWS_POWEROFF_SAME_TIME` | `1` | board_cfg.h | Both buds power off together |
| `CONFIG_TWS_AUTO_PAIR_WITHOUT_UNPAIR` | `1` | board_cfg.h | Re-pair without explicit unlink |
| `TCFG_USER_BLE_ENABLE` | `1` | board_cfg.h | BLE enabled |
| `RCSP_ADV_EN` | `1` | board_cfg.h | RCSP advertisement enabled |
| `JL_EARPHONE_APP_EN` | `1` | board_cfg.h | Jieli app protocol |
| `RCSP_UPDATE_EN` | `1` | board_cfg.h | OTA updates via RCSP |
| `USER_SUPPORT_PROFILE_HFP` | `1` | board_cfg.h | Hands-free calls |
| `USER_SUPPORT_PROFILE_A2DP` | `1` | board_cfg.h | Music streaming |
| `USER_SUPPORT_PROFILE_AVCTP` | `1` | board_cfg.h | Media controls |
| `USER_SUPPORT_PROFILE_HID` | `1` | board_cfg.h | HID (volume, play buttons) |
| `USER_SUPPORT_PROFILE_PNP` | `1` | board_cfg.h | Plug and Play ID |
| `BT_INBAND_RINGTONE` | `1` | board_cfg.h | Phone ringtone in earphone |
| `BT_SUPPORT_DISPLAY_BAT` | `1` | board_cfg.h | Battery shown on phone |
| `BT_SUPPORT_MUSIC_VOL_SYNC` | `1` | board_cfg.h | Volume sync phone↔earphone |
| `TCFG_MANUAL_MAC_PROVISIONING_ENABLE` | `1` | user_cfg.c | 5 pairs hardcoded |
| `CONFIG_BT_RX_BUFF_SIZE` | `46 KB` | board_cfg.h | LDAC needs large buffer |
| `TCFG_AUTO_SHUT_DOWN_TIME` | `180 s` | board_cfg.h | 3-min auto-off when idle |

---

## Section 5 — Connection / BT Features DISABLED ⛔ (Improvement Candidates)

| Flag / Setting                       | Value                                   | File               | Improvement Doc                                                                                                     |
| ------------------------------------ | --------------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------- |
| `OTA_TWS_SAME_TIME_ENABLE`           | `0`                                     | board_cfg.h        | [CONN-IMP-001](./CONNECTION%20IMPROVEMENTS/CONN-IMP-001%20—%20Simultaneous%20TWS%20OTA%20Double-Bank%20Flash.md)    |
| `CONFIG_DOUBLE_BANK_ENABLE`          | `0`                                     | global_build_cfg.h | [CONN-IMP-001](./CONNECTION%20IMPROVEMENTS/CONN-IMP-001%20—%20Simultaneous%20TWS%20OTA%20Double-Bank%20Flash.md)    |
| `USER_SUPPORT_PROFILE_SPP`           | `0`                                     | board_cfg.h        | [CONN-IMP-002](./CONNECTION%20IMPROVEMENTS/CONN-IMP-002%20—%20SPP%20Profile%20Enable.md)                            |
| `USER_SUPPORT_PROFILE_PBAP`          | `0`                                     | board_cfg.h        | [CONN-IMP-003](./CONNECTION%20IMPROVEMENTS/CONN-IMP-003%20—%20PBAP%20Phone%20Book%20Access%20Profile.md)            |
| `TCFG_LOWPOWER_LOWPOWER_SEL`         | `0`                                     | board_cfg.h        | [CONN-IMP-004](./CONNECTION%20IMPROVEMENTS/CONN-IMP-004%20—%20Low%20Power%20Mode%20Enable.md)                       |
| `TCFG_AUTO_SHUT_DOWN_TIME`           | `180 s` (may be too long/short)         | board_cfg.h        | [CONN-IMP-005](./CONNECTION%20IMPROVEMENTS/CONN-IMP-005%20—%20Auto-Shutdown%20Timer%20Tuning.md)                    |
| `CONFIG_TWS_CONNECT_SIBLING_TIMEOUT` | `4 s` (may be too short)                | board_cfg.h        | [CONN-IMP-006](./CONNECTION%20IMPROVEMENTS/CONN-IMP-006%20—%20TWS%20Sibling%20Reconnect%20Optimization.md)          |
| BT clock table                       | idle 24MHz, connected 48MHz, A2DP 96MHz | board_cfg.h        | [CONN-IMP-007](./CONNECTION%20IMPROVEMENTS/CONN-IMP-007%20—%20BT%20Clock%20Frequency%20Power%20vs%20Performance.md) |

---

## Section 6 — Connection Features DISABLED ⛔ (Out of Scope)

| Flag / Setting        | Value                    | Reason Excluded              |
| --------------------- | ------------------------ | ---------------------------- |
| Multi-point (2 phone) | `TCFG_BD_NUM=1` when TWS | TWS forces single-phone mode |
| aptX / aptX-HD        | not in codec list        | SDK library not included     |
| LE Audio (broadcast)  | no BLE ISO               | Chip stack limitation        |

---

## System Constants (Read-Only Reference)

| Setting | Value |
|---|---|
| Chip | AC701N (JL7016G Hybrid) |
| Flash | 1 MB |
| SDK Version | JL701N_V1.6.1 |
| System Clock | 24 MHz base, 96 MHz max |
| RAM retained (low power) | 384 KB (3 × 128 KB) |
| BT Spec | BR 5.1 + EDR + BLE 5.x |
| DAC SNR | ≥ 95 dB |
| ADC SNR | ≥ 90 dB |
| Microphone (ZTS6216) | 38 dB SPL, 65 dB S/N, 1.5–3.6 V |
