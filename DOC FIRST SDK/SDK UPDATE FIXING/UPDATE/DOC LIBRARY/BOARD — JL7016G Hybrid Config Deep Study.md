---
tags: [board, config, pinout, features]
date: 2026-04-22
board: JL7016G Hybrid
chip: AC701N (BR28)
---

# JL7016G Hybrid — Board Configuration Deep Study

**Config file:** `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h`  
**Global build cfg:** `apps/earphone/board/br28/board_jl7016g_hybrid_global_build_cfg.h`  
**Active variant macro:** `CONFIG_BOARD_JL7016G_HYBRID`  
**Client board:** `EARPHONE_HYBRID` (0x02) — JL7016G Hybrid + Dual-MIC ENC TWS standard schematic  

---

## 1. UART / Debug

| Config | Value | Note |
|--------|-------|------|
| UART0 | ENABLED | Debug print |
| TX Port | `IO_PORTB_05` | Earphone Hybrid board |
| RX Port | `NO_CONFIG_PORT` | Print-only, no RX needed |
| Baud rate | 115200 | |

---

## 2. IIC (I2C)

| Config | Value |
|--------|-------|
| SW IIC CLK | `IO_PORTA_09` |
| SW IIC DAT | `IO_PORTA_10` |
| SW IIC Delay | 50 counts |
| HW IIC Port | `'B'` → SCL: `IO_PORTA_09`, SDA: `IO_PORTA_10` |
| HW IIC Clock | 100 kHz |

---

## 3. Keys

### IO Key
| Config | Value |
|--------|-------|
| IO Key | ENABLED |
| Port | `IO_PORTB_01` |
| Connect way | ONE_PORT_TO_LOW (active low) |

### Other Keys
| Key Type | Status |
|----------|--------|
| AD Key | DISABLED |
| IR Key | DISABLED |
| LP Touch Key | DISABLED |

## 8A. Output Volume Ceiling Fix

### What was limiting loudness

On this board, ANC is enabled, so the effective playback ceiling is controlled by the software digital volume generator rather than only by the visible volume-step count. The important limit is in `cpu/br28/audio_config.h`:

- `MAX_DIG_VOL = 16` defines the number of volume levels.
- `DIG_VOL_MAX_VALUE` defines the top gain those levels can actually reach.

Before the fix, `TCFG_AUDIO_DAC_MODE == DAC_MODE_L_DIFF` forced:

- `DIG_VOL_MAX_VALUE = -17.0f`

That meant the product could still show full volume while the actual playback ceiling remained heavily attenuated.

### Fix applied

A board-specific override was added for `CONFIG_BOARD_JL7016G_HYBRID` when ANC is enabled:

```c
#elif defined(CONFIG_BOARD_JL7016G_HYBRID) && (TCFG_AUDIO_ANC_ENABLE)
#define DIG_VOL_MAX_VALUE       (-6.0f)
```

### Why `-6 dB` and not higher

The SDK already documents the ANC-safe limit directly below this setting:

> When ANC is enabled, digital volume above `-6 dB` can cause music distortion.

So this fix raises the board to the highest level the SDK itself marks as safe, without pushing into the known distortion region.

### Practical result

- The board is now noticeably louder at maximum volume.
- The change is narrow and board-specific.
- Other boards keep their original volume policy.
- This does not change the number of user volume steps; it changes the real top-end gain those steps map to.
| PLCNT Touch Key | DISABLED |
| RDEC Key | DISABLED |

---

## 4. Audio — DAC

| Config | Value | Note |
|--------|-------|------|
| DAC | ENABLED | |
| Connect mode | `DAC_OUTPUT_MONO_L` | Left channel mono |
| DAC mode | `DAC_MODE_L_DIFF` | Low-voltage differential |
| HPVDD external | ENABLED | Boost DAC output amplitude |
| HPVDD port | `IO_PORTG_06` | Earphone Hybrid board |
| DAC PA port | `NO_CONFIG_PORT` | Not used |

---

## 5. Audio — ADC / MIC

| Config | Value | Note |
|--------|-------|------|
| ADC | ENABLED | |
| Line channel | `AUDIO_ADC_LINE0` | |
| LDO current | 3 (2.5µA) | |
| MIC power source | `MIC_PWR_FROM_MIC_BIAS` | Internal MICBIAS on PA2 (PA0 path disabled) |
| MIC LDO | DISABLED | `TCFG_AUDIO_MIC_LDO_EN` not active under current power mode |
| MIC0 mode | `AUDIO_MIC_CAP_MODE` | Single-ended cap mode for main call MIC (PA1) |
| MIC1/MIC2 mode | `AUDIO_MIC_CAP_DIFF_MODE` | Differential mode kept for ANC microphones |
| PDM MIC SCLK | `IO_PORTA_07` | |
| PDM MIC DAT0 | `IO_PORTA_08` | |
| PDM MIC DAT1 | `NO_CONFIG_PORT` | Not used |
| Active MIC channel | `AUDIO_ADC_MIC_0` | Single mic (dual mic disabled) |
| Dual MIC (ENC) | DISABLED | |
| Triple MIC | DISABLED | |

---

## 6. ANC (Active Noise Cancellation)

| Config | Value | Note |
|--------|-------|------|
| ANC | ENABLED | Controlled by `CONFIG_ANC_ENABLE = 1` in global build cfg |
| ANC type | `ANC_HYBRID_EN` | Hybrid (FF + FB) |
| ANC channel | `ANC_L_CH` | Left channel only |
| FF MIC (Left) | `A_MIC1` | Feed-forward microphone |
| FB MIC (Left) | `A_MIC2` | Feed-back microphone |
| FF MIC (Right) | `MIC_NULL` | Not used |
| FB MIC (Right) | `MIC_NULL` | Not used |
| ANC tool debug | DISABLED | |
| ANC ear adaptive | DISABLED | |
| ANC wind noise detect | DISABLED | |
| Speak-to-chat | DISABLED | |
| Wide-area tap | DISABLED | |

---

## 7. CVP (Clear Voice Processing)

| Config | Value | Note |
|--------|-------|------|
| CVP NS mode | `CVP_DNS_MODE` | Neural network noise reduction |
| CVP develop | DISABLED | Using JL built-in algo |
| AEC online debug | DISABLED | |
| DMS mode | `DMS_NORMAL` | Standard dual-mic mode |
| DMS master MIC | `MIC0` | |

---

## 8. EQ

| Config | Value |
|--------|-------|
| EQ total | ENABLED |
| BT music EQ | ENABLED |
| Phone (call) EQ | ENABLED |
| EQ from file | ENABLED (offline config file) |
| EQ sections max | 10 |
| Call DL EQ sections | 3 |
| Call UL EQ sections | 3 |
| Online EQ debug | DISABLED |
| EQ effect tool | DISABLED |

---

## 9. Bluetooth

| Config                | Value              |
| --------------------- | ------------------ |
| TWS                   | ENABLED            |
| BLE                   | ENABLED            |
| AAC                   | DISABLED           |
| LDAC                  | DISABLED           |
| Connected devices     | 1 (TWS mode)       |
| SPP                   | DISABLED (default) |
| HFP                   | ENABLED            |
| A2DP                  | ENABLED            |
| AVCTP                 | ENABLED            |
| HID                   | ENABLED            |
| PNP                   | ENABLED            |
| PBAP                  | DISABLED           |
| Inband ringtone       | ENABLED            |
| Phone number announce | DISABLED           |
| Battery display       | ENABLED            |
| Music volume sync     | ENABLED            |
| BT RX buffer          | 22 KB              |

---

## 10. Charger / Charge Store

| Config                 | Value                               | Note                   |
| ---------------------- | ----------------------------------- | ---------------------- |
| Charge (internal)      | ENABLED                             |                        |
| Charge full voltage    | `CHARGE_FULL_V_4199`                | 4.199 V                |
| Charge full current    | `CHARGE_FULL_mA_10`                 | 10 mA                  |
| Charge current         | `CHARGE_mA_40`                      | 40 mA constant current |
| Trickle current        | `CHARGE_mA_10`                      |                        |
| Charge on power-on     | DISABLED                            |                        |
| Charge → auto power-on | DISABLED                            |                        |
| Smart charge store     | DISABLED                            |                        |
| Test box               | ENABLED                             |                        |
| ANC test box           | ENABLED (follows CONFIG_ANC_ENABLE) |                        |
| UMIDIGI charge box     | ENABLED                             | 20ms/bit timing        |
| Charge store port      | `IO_PORTP_00`                       |                        |

---

## 11. LED

| Config | Value |
|--------|-------|
| PWM LED | ENABLED |
| LED mode | `LED_ONE_IO_MODE` (single IO) |
| LED pin | `IO_PORTG_05` |

---

## 12. Clock

| Config | Value |
|--------|-------|
| Clock source | `SYS_CLOCK_INPUT_PLL_BT_OSC` |
| System clock | 24 MHz |
| OSC crystal | 24 MHz |
| Clock mode | `CLOCK_MODE_ADAPTIVE` |

---

## 13. Power

| Config | Value |
|--------|-------|
| Power mode | `PWR_LDO15` (LDO, not DCDC) |
| BTOSC low-power disable | 0 (keep BTOSC) |
| Low-power enable | 0 (disabled) |
| VDDIOM level | `VDDIOM_VOL_30V` (3.0V) |
| Low-power OSC | `OSC_TYPE_LRC` |
| RAM power-down size | 3 (×128K) |

---

## 14. Flash / OTA

| Config | Value |
|--------|-------|
| Flash size | 1 MB |
| OTA (RCSP/JL-OTA) | ENABLED |
| Double bank | DISABLED (single bank) |
| VM size minimum | 8 KB |
| VM erase on update | NO (preserve) |
| BTIF erase on update | NO (preserve) |
| MD5 check on update | DISABLED |

---

## 15. IMU Sensor

| Config | Value | Note |
|--------|-------|------|
| IMUSENSOR | DISABLED | No IMU hardware on JL7016G |
| ICM42670P | DISABLED | |
| MPU6887P | DISABLED | |
| QMI8658 | DISABLED | |
| LSM6DSL | DISABLED | |
| MPU6050 | DISABLED | |
| IMU power port | `NO_CONFIG_PORT` | **Added by FIX-001** |

---

## 16. G-Sensor / IR Sensor

| Config | Value |
|--------|-------|
| G-Sensor | DISABLED |
| DA230 | DISABLED |
| SC7A20 | DISABLED |
| STK8321 | DISABLED |
| IR Sensor | DISABLED |
| JSA1221 | DISABLED |

---

## 17. Ear Detection

| Config                    | Value         |
| ------------------------- | ------------- |
| External ear detect       | DISABLED      |
| LP touch ear detect       | DISABLED      |
| External touch power port | `IO_PORTC_03` |
| External touch EN port    | `IO_PORTC_04` |

---

## 18. Disabled / Not Used Features

| Feature                         | Status   |
| ------------------------------- | -------- |
| Smart voice / KWS               | DISABLED |
| IIS input/output                | DISABLED |
| SD card                         | DISABLED |
| Hearing aid (DHA)               | DISABLED |
| Sidetone                        | DISABLED |
| Audio data export (SPP/SD/UART) | DISABLED |
| FM emitter                      | DISABLED |
| Line-in                         | DISABLED |
| USB CDC config tool             | DISABLED |
| DRC                             | DISABLED |
| AI/ASR                          | DISABLED |

---

## 19. Build Metadata Fix Notes

| Item                             | Status   | Note                                                                                                                                                                                                |     |
| -------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --- |
| IMU power macro                  | FIXED    | `TCFG_IMU_SENSOR_PWR_PORT` added for JL7016G (see FIX-001)                                                                                                                                          |     |
| gSensor LIS2DE12 driver naming   | FIXED    | Corrected `lis2dh12_*` typo to `lis2de12_*` in project and linker object list (see FIX-002)                                                                                                         |     |
| Online DB / FFT-PCA link symbols | FIXED    | Added `fft_and_pca` into active project/link list and added non-debug stubs for online DB APIs to remove undefined refs (see FIX-003)                                                               |     |
| TWS L/R hardware channel split   | VERIFIED | With `CONFIG_TWS_CHANNEL_SELECT = CONFIG_TWS_EXTERN_DOWN_AS_LEFT`, `PC5` level decides side. Real-board validation succeeded only after one unit had pull-down and the other pull-up (see FIX-004). |     |

---

## 20. TWS Auto Pairing Validation (Real Hardware)

### Config Basis

- TWS enabled at board config: `TCFG_USER_TWS_ENABLE = 1`
- Auto pairing selected: `CONFIG_TWS_PAIR_MODE = CONFIG_TWS_PAIR_BY_AUTO`
- Channel select mode: `CONFIG_TWS_CHANNEL_SELECT = CONFIG_TWS_EXTERN_DOWN_AS_LEFT`
- Channel detect pin: `CONFIG_TWS_CHANNEL_CHECK_IO = IO_PORTC_05`

### Runtime Mechanism

- At boot, `set_channel_by_code_or_res()` samples `PC5` and resolves local channel.
- For `CONFIG_TWS_EXTERN_DOWN_AS_LEFT`, the logic is:
	- `PC5` low => `'L'`
	- `PC5` high => `'R'`

### Bench Validation Result

- Same firmware was programmed to both boards.
- TWS did not form until hardware L/R split was present on `PC5`.
- Verified working condition:
	- Board A: `PC5` pull-down
	- Board B: `PC5` pull-up
- Under this condition, TWS auto pairing and normal operation were confirmed.

---

## Pin Summary Table

| Pin           | Function                                        |
| ------------- | ----------------------------------------------- |
| `IO_PORTB_01` | IO Key                                          |
| `IO_PORTB_05` | UART0 TX (debug)                                |
| `IO_PORTA_09` | IIC CLK (SW & HW)                               |
| `IO_PORTA_10` | IIC DAT (SW & HW)                               |
| `IO_PORTA_07` | PDM MIC SCLK                                    |
| `IO_PORTA_08` | PDM MIC DAT0                                    |
| `IO_PORTG_05` | PWM LED                                         |
| `IO_PORTG_06` | HPVDD power enable                              |
| `IO_PORTC_05` | TWS channel detect input (`CONFIG_TWS_CHANNEL_CHECK_IO`) |
| `IO_PORTC_03` | External touch power (TP_PWR)                   |
| `IO_PORTC_04` | External touch EN (TP_EN)                       |
| `IO_PORTP_00` | Charge store / test box comms                   |
| `IO_PORTA_00` | MIC LDO pin available in SoC, not used for main MIC on this board |
| `IO_PORTA_01` | Main MIC0 analog input (call uplink)            |
| `IO_PORTA_02` | MICBIAS output for MIC0 power under current config |
| `IO_PORTA_12` | IIS MCLK (configured but IIS disabled)          |
| `IO_PORTA_13` | IIS SCLK (configured but IIS disabled)          |
| `IO_PORTA_14` | IIS LRCLK (configured but IIS disabled)         |
| `IO_PORTA_15` | IIS DATA0 (configured but IIS disabled)         |
| `IO_PORT_DP`  | USB DP (online tool TX if enabled)              |
| `IO_PORT_DM`  | USB DM (online tool RX if enabled)              |
| `LDO pin`     | Reset (hold 4s, active high)                    |
| `PB01`        | Reset1 (hold 8s, active low, if IO key enabled) |

---

## Related FIX Records

| Fix | Title | Relevance |
|-----|-------|-----------|
| [FIX-001](../../FIXING/FIX-001%20—%20TCFG_IMU_SENSOR_PWR_PORT%20Undeclared.md) | `TCFG_IMU_SENSOR_PWR_PORT` undeclared | Board config macro fix |
| [FIX-012](../../FIXING/FIX-012%20—%20MIC%20power%20PA0%20unconnected%20switched%20to%20PA2%20MICBIAS.md) | MIC power PA0 → PA2 MICBIAS | Board pinout — MIC wiring |
| [FIX-013](../../FIXING/FIX-013%20—%20MIC0%20differential%20mode%20mismatch%20changed%20to%20single-ended.md) | MIC0 single-ended | Board config — MIC mode |
| [FIX-015](../../FIXING/FIX-015%20—%20PB1_COMPLETE_SOLUTION.md) | PB1 complete solution | Board config — CH1/PB1 threshold and role |
