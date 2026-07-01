# CONFIG GUI FIELD REFERENCE — Every Tab, Every Option Explained

**Tool:** SDK_Config — JieLi `luaconfig` (v2.0.47, earphone-1.2.0)  
**Board:** JL7016G Hybrid (AC701N / BR28 core)  
**Output file:** `cfg_tool.bin` (packed into flash alongside firmware)  
**Accessed via:** `cpu/br28/tools/AC701N_配置工具入口(Config Tools Entry).jlxproj` → Config Tool button

> **How to save and apply**: Use the top-right **Save** button in the GUI. This writes `cfg_tool.bin`. For the changes to take effect on-device, reflash with the identity-clean script (or normal flash if you have already cleared persistent data).

---

## Tab Overview

| #   | Tab Name          | What It Controls                                             |
| --- | ----------------- | ------------------------------------------------------------ |
| 1   | BT Config         | Bluetooth names, MAC addresses, RF power, BLE settings       |
| 2   | Common Config     | Auto shutdown, LED events, tone events, charge settings      |
| 3   | Call Config       | CVP microphone processing (AEC, NS, AGC, NLP, EQ, gain)      |
| 4   | Microphone Config | MIC mode selection, hardware bias, LDO voltage               |
| 5   | Tone File Config  | Assign audio tone files to device events                     |
| 6   | Volume Config     | Volume table design for music and call (MeanStep, FixedStep) |
| 7   | ANC Config        | Active Noise Cancellation hardware parameters                |
| 8   | Device Info       | PID, VID, SDK version, checksum (read-only or meta)          |

---

## Tab 1 — BT Config

Controls Bluetooth classic (EDR) and BLE identity and RF power.

### Section: BT Names

| Field | Description | Current Value | Where it Goes |
|-------|-------------|---------------|----------------|
| BT Name (slot 1) | Primary EDR Bluetooth device name. This is what your phone sees when scanning. | `ibrarkhan` | `CFG_BT_NAME` → `bt_cfg.edr_name` |
| BT Name (slots 2–20) | Alternate/fallback name slots (not used unless multi-name feature enabled). | `jl_earphone_2` … `jl_earphone_20` | Same table |
| BLE Name | BLE advertisement name. If blank, defaults to BT Name. | `jl_earphone_ble` | `CFG_BLE_NAME` → `bt_cfg.ble_name` |
| Name Switch 1–20 | Enable/disable each name slot. Switch 1 is ON (1), rest are OFF (0). | 1 / 0 | Name active flag |

> **Note:** If you only want one device name, fill slot 1 and leave all others as default. Keep Switch 1 = 1.

### Section: MAC Addresses

| Field | Description | Current Value |
|-------|-------------|---------------|
| Classic BT MAC (经典蓝牙MAC地址) | EDR Bluetooth MAC. The 6-byte hardware address for BR/EDR. | `{60,0,10,126,26,0}` (hex: `3C:00:0A:7E:1A:00`) |
| BLE MAC (低功耗蓝牙MAC地址) | BLE Bluetooth MAC. Used for BLE advertisement if code reads it. | `{76,0,10,35,31,18}` (hex: `4C:00:0A:23:1F:12`) |

> **Important:** As of FIX-005, the firmware now reads `CFG_BLE_MAC_ADDR` at boot. If this field is all-FF (blank) or all-zero, it falls back to deriving BLE MAC from EDR MAC automatically.

### Section: RF Power

| Field | Description | Typical Value |
|-------|-------------|---------------|
| Classic BT TX Power (经典蓝牙发射功率) | EDR transmit power level (0–10). Higher = longer range, higher current draw. | `10` |
| BLE TX Power (低功耗蓝牙发射功率) | BLE transmit power level (0–10). | `10` |

> `bt_max_pwr_set(app_var.rf_power, 5, 8, 9)` in user_cfg.c applies these values.

### Section: TWS / Pairing

| Field | Description | Value |
|-------|-------------|-------|
| TWS Pair Code (对耳配对码) | 2-byte TWS device pair identifier. Both earbuds must match to pair together. | `0xFFFF` (65535 = any) |
| Pin Code | Classic BT PIN code (legacy, not used in SSP). | blank |

---

## Tab 2 — Common Config

Controls device behaviour events, auto-shutdown, and charge-related settings.

### Section: Auto Shutdown

| Field | Description | Value |
|-------|-------------|-------|
| Auto shutdown (no connection) — 没有连接自动关机时间配置 | Minutes of no-connection before auto power off. `0` = disabled. | `3` min |

### Section: LED Events (LED indicators per state)

Each event has an LED pattern code. `255` = no LED change / use default behavior.

| Event | LED Code | Meaning |
|-------|----------|---------|
| Power On (开机) | `3` | LED pattern 3 on power on |
| Power Off (关机) | `21` | LED pattern 21 on power off |
| BT Init Complete (蓝牙初始化完成) | `16` | LED blink pattern 16 during BT init |
| BT Connected (蓝牙连接成功) | `1` | Solid or blink once |
| BT Disconnected (蓝牙断开连接) | `15` | LED pattern 15 |
| TWS Connected (对耳连接成功) | `15` | |
| TWS Disconnected (对耳断开连接) | `16` | |
| Incoming Call (来电) | `255` | No change |
| Call In Progress (通话中) | `255` | No change |
| Outgoing Call (去电) | `255` | No change |
| Low Battery (低电) | `14` | |
| Max Volume (最大音量) | `255` | No change |
| Charging Start (开始充电) | `9` | |
| Charging Complete (充电完成) | `3` | |

> LED codes correspond to patterns defined in the LED management module in firmware.

### Section: Tone Events (Audio feedback per state)

Each event has a tone index matching the tone file loaded in the Tone File Config tab.

| Event | Tone Index | Mapped Tone File |
|-------|------------|-----------------|
| Power On (开机TONE) | `17` | `power_on.wts` |
| Power Off (关机TONE) | `16` | `power_off.wts` |
| BT Init (蓝牙初始化完成TONE) | `10` | `bt.wts` |
| BT Connected | `11` | `bt_conn.wts` |
| BT Disconnected | `12` | `bt_dconn.wts` |
| TWS Connected | `13` | |
| TWS Disconnected | `14` | |
| Incoming Call | `18` | `ring.wts` |
| Low Battery | `15` | `low_power.wts` |
| Max Volume | `19` | `vol_max.wts` |
| Call In Progress | `255` | (none) |
| Outgoing Call | `255` | (none) |
| Charging Start | `255` | (none) |
| Charging Complete | `255` | (none) |

### Section: Charge Configuration (充电配置)

| Field | Description | Value |
|-------|-------------|-------|
| 充电配置使能开关 | Enable charge config | `1` (enabled) |
| 充电电流 | Charge current setting | `3` |
| 充电满电流 | Full-charge cutoff current | `3` |
| 充电满电压 | Full-charge cutoff voltage | `8` |
| 低电提醒电压 | Low battery warning voltage | `340` (3.40V × 100) |
| 低电关机电压 | Low battery shutdown voltage | `330` (3.30V × 100) |
| 开机充电使能 | Boot while charging enable | `0` |

---

## Tab 3 — Call Config

Controls the **CVP (Call Voice Processing)** chain — what happens to your microphone signal during phone calls.

> The tool has sub-modes based on mic count: 1-mic (single), 2-mic (DMS), 3-mic (TMS). Active mode is selected by your board's `TCFG_AUDIO_TRIPLE/DUAL/SINGLE_MIC_ENABLE` defines.

### CVP Processing Enable Flags (applies per mode)

| Parameter | Meaning | Your Value |
|-----------|---------|------------|
| AEC (Acoustic Echo Cancellation) | Removes speaker audio leaking into MIC | `0` (off) |
| NS (Noise Suppression) | Reduces background noise | `1` (on) |
| AGC (Automatic Gain Control) | Keeps mic level consistent | `1` (on) |
| NLP (Non-Linear Processor) | Removes residual echo after AEC | `1` (on) |
| EQ (Equalizer) | Apply mic EQ curve | `1` (on) |

### Key CVP Level Parameters

| Parameter | Meaning | Your Value |
|-----------|---------|------------|
| MIC Gain | Microphone input gain in the processing chain | `8` |
| DAC Gain | Speaker/reference signal gain for AEC | `8` |
| AEC Mode | AEC algorithm variant (22 = standard, 30 = DMS mode) | `22` |
| ECHO_PRESENT_THR | Echo detection threshold (dB, negative). Lower = more sensitive. | `-70.0 dB` |
| AEC_REFENGTHR | Reference energy threshold for AEC | `-70.0 dB` |
| AEC_DT_AGGRESS | Double-talk AEC aggressiveness (1.0 = neutral) | `1.0` |

### NLP / Fade Parameters

| Parameter | Meaning | Your Value |
|-----------|---------|------------|
| NLP_MIN_SUPPRESS | Minimum NLP suppression floor | `4.0` |
| NLP_AGGRESS_FACTOR | NLP aggressiveness factor | `-3.0` |
| DT_FADE_IN / OUT | Double-talk fade time (seconds) | `1.3 / 1.3` |
| NDT_FADE_IN / OUT | Non-double-talk fade time | `1.3 / 1.3` |
| DT_SPEECH_THR | Double-talk speech threshold | `-40.0 dB` |
| NDT_SPEECH_THR | Non-double-talk threshold | `-50.0 dB` |
| DT_MAX/MIN_GAIN | Double-talk gain range | `12.0 / 0.0` |
| NDT_MAX/MIN_GAIN | Non-double-talk gain range | `8.0 / 4.0` |

### ANS Parameters (Adaptive Noise Suppression, used in some modes)

| Parameter | Your Value |
|-----------|------------|
| ANS_AGGRESS | `1.25` |
| ANS_SUPPRESS | `0.09` |

---

## Tab 4 — Microphone Config

Hardware MIC topology and analog front-end settings.

| Field | Description | Value |
|-------|-------------|-------|
| MIC Mode (MIC模式选择) | 1 = single MIC, 2 = dual MIC (DMS), 3 = triple MIC (TMS) | `1` |
| Bias Resistor (偏置电阻选择) | Microphone bias resistor selection index (hardware). Affects MIC sensitivity and noise floor. | `4` |
| MIC LDO Voltage (MICLDO电压选择) | MIC power supply LDO voltage level. Affects headset/analog MIC compatibility. | `5` |

> When using dual-MIC mode (`cvp.2mic.*`), additional parameters become active:
> - `MIC_Distance` / `Mic_Distance:float` — physical distance between the two mics (15 mm = 0.015 m default)
> - `SIR_MaxFreq` — max beamforming frequency (3000 Hz)
> - `AF_Length` — adaptive filter tap length (128)

---

## Tab 5 — Tone File Config

Maps audio feedback tone files (`.wts` format) to numbered tone slots. These slots are referenced by the event tone codes in Common Config.

| Slot/Index | Event Name | Tone File Path |
|------------|-----------|----------------|
| 0–9 | Numeric slots (custom use) | `extra_tones/0.wts` … `9.wts` |
| `bt` (10) | Bluetooth init sound | `extra_tones/bt.wts` |
| `bt_conn` (11) | BT connected | `extra_tones/bt_conn.wts` |
| `bt_dconn` (12) | BT disconnected | `extra_tones/bt_dconn.wts` |
| `low_power` (15) | Low battery warning | `extra_tones/low_power.wts` |
| `power_off` (16) | Power off sound | `extra_tones/power_off.wts` |
| `power_on` (17) | Power on sound | `extra_tones/power_on.wts` |
| `ring` (18) | Incoming call ring | `extra_tones/ring.wts` |
| `vol_max` (19) | Max volume alert | `extra_tones/vol_max.wts` |
| `music` (22) | Music mode indicator | `extra_tones/music.wts` |
| `pc` (26) | PC/USB mode indicator | `extra_tones/pc.wts` |
| ANC On (27) | ANC enable feedback | `extra_tones/anc_on.wts` |
| ANC Off (27) | ANC disable feedback | `extra_tones/anc_off.wts` |
| Transparency (27) | Transparency mode feedback | `extra_tones/anc_trans.wts` |

> `.wts` files are JieLi-format audio waveform tone files. Use the Tone editor tool to create/replace them.  
> All paths shown are under `cpu/br28/tools/extra_tones/`.

---

## Tab 6 — Volume Config

Shown in the screenshot attached by user. Designs the volume table used by the firmware DAC driver.

### Volume Type (顶部下拉)

| Option | Description |
|--------|-------------|
| **Combined Volume** (合并音量) | Single unified volume table used for both music and call — simplest setup. |
| System Volume Only | Separate table only for music playback. |
| Call Volume Only | Separate table only for phone calls. |

**Fixed Analog Gain** checkbox — when checked, analog gain is fixed and only digital volume changes. Useful to avoid analog pop sounds.

---

### Sub-Tab: System Volume / Call Volume

Both sub-tabs contain the same two section types:

---

#### Configuration (MeanStep) — 均匀步长配置

Generates a volume table by dividing the range evenly.

| Field | What It Does | Your Values |
|-------|-------------|-------------|
| **Total Level** | Number of volume steps (1–100). Firmware volume control goes from level 0 to this value. | `31` steps |
| **Max Volume** | Top of the volume range in dB. `0.0` = digital full scale, no attenuation. | `0.0 dB` |
| **Min Volume** | Bottom of the range in dB. `-50.0` = very quiet. | `-50.0 dB` |
| **Generate** button | Calculates and fills the Configuration Output table automatically. | Click after changing values |
| **Dump Configuration Results** button | Shows the raw dB-per-step values for inspection. | Optional |

**How MeanStep works:**  
The range from `Min` to `Max` is divided into `Total Level` equal steps. Each step = `(Max - Min) / (TotalLevel - 1)`.  
With 31 levels from -50 to 0: each step ≈ 1.67 dB.

---

#### Configuration (FixedStep) — 固定步长配置

Generates a volume table using a fixed dB step per level.

| Field | What It Does | Your Values |
|-------|-------------|-------------|
| **Volume Step** | Fixed dB increment per step. | `2.00 dB` |
| **Max Volume** | Upper limit of the table. | `0.0 dB` |
| **Min Volume** | Lower limit. Table stops generating at this floor. | `-50.0 dB` |
| **Generate** button | Fills output table using: level N = Max - (N × Step). | Click after changing |
| **Dump Configuration Results** | Inspect generated levels. | Optional |

**How FixedStep works:**  
Starting from Max, each level down = previous level − Step.  
With step=2.0, Max=0: levels = 0, -2, -4, -6, … -50 (26 total levels).

---

#### Configuration Output (配置输出)

The output grid shows the actual dB table that gets written to `cfg_tool.bin`.

| Column | Description |
|--------|-------------|
| **Switch** checkbox | Enable/disable this specific volume step. Unchecked levels are skipped. |
| **Expected Volume N** | Target dB value for level N. Can be manually overridden after Generate. |

> The output table is read by firmware via `CFG_SYS_VOL_ID` / `CFG_CALL_VOL_ID` syscfg IDs, which are applied to the digital volume ramp in the DAC chain.

---

### Call Volume Sub-Tab

Same structure as System Volume. Separate table for call audio — lets you have different loudness behavior during phone calls vs. music playback.

Your state file shows:
- **System Volume** (comvol table 1): 31 levels, 0 to -50 dB  
- **Call Volume** (comvol table 2): 15 levels, -14 to -45 dB

---

## Tab 7 — ANC Config

Controls the Active Noise Cancellation DSP hardware parameters. These values are written to `cfg_tool.bin` and applied at ANC init.

### ANC Mode Topology

| Parameter | Meaning | Value |
|-----------|---------|-------|
| analogm (ANCalogm) | ANC analog mode selection (FF/FB/hybrid topology) | `5` |
| trans_alogm | Transparency mode analog topology | `3` |
| gain_sign | Invert gain polarity (0=normal, 1=inverted) | `0` |
| ahs_en | ANC headset mode enable | `1` |
| drc_en | DRC (Dynamic Range Control) for ANC enable | `0` |
| cmp_en | Compander enable in ANC chain | `1` |

### Gain Settings (Left and Right channels independently)

| Parameter | Description | L Value | R Value |
|-----------|-------------|---------|---------|
| ffgain | Feedforward gain (linear, 1.0 = unity) | `1.0` | `1.0` |
| fbgain | Feedback gain | `1.0` | `1.0` |
| transgain | Transparency passthrough gain | `1.0` | `1.0` |
| cmpgain | Compander gain | `1.0` | `1.0` |
| ffmic_gain | FF microphone preamplifier gain code | `4` | `4` |
| fbmic_gain | FB microphone preamplifier gain code | `4` | `4` |

> `/show` variants (e.g., `fbgain:/show`) are display-only values in dB, converted from the linear gain for readability. Not saved directly.

### Shared ANC Parameters

| Parameter | Description | Value |
|-----------|-------------|-------|
| dac_gain | DAC output gain in ANC chain | `3` |
| noise_lvl | Ambient noise level estimation mode | `0` |
| fade_step | ANC gain fade step size (smoother on/off transitions) | `1` |
| fb_2nd_dcc | FB second-order DC correction coefficient | `4` |
| ff_2nd_dcc | FF second-order DC correction coefficient | `4` |
| ahs_wn_shift | White noise shift factor for AHS | `9` |

### DRC (Dynamic Range Control) Settings

DRC has three zones: feedback, feedforward, and transparency. Each has:

| Parameter Template | Description | Example (fb) |
|-------------------|-------------|--------------|
| drc*_lthr | Low threshold (linear raw value) | `0` |
| drc*_hthr | High threshold | `6000` |
| drc*_lgain | Low-zone gain | `1024` (= 0 dB in Q10 format) |
| drc*_hgain | High-zone gain | `513` (≈ -6 dB) |
| drc*_norgain | Normal-zone gain | `1024` |
| drc_dcc_det_time | DCC detection time (ms) | `200` |
| drc_dcc_res_time | DCC reset time (ms) | `10` |
| drc_ff_2dcc / drc_fb_2dcc | Enable second-order DCC in DRC | `0` |

> Gain values use Q10 fixed-point: `1024 = 1.0`, `513 ≈ 0.5 = -6 dB`.

---

## Tab 8 — Device Info

Read-only or metadata fields used for device identification and OTA compatibility checking.

| Field | Description |
|-------|-------------|
| `*device-info-pid*` | Product ID (matches `isd_config.ini` PID). Must match between GUI and flash for OTA to accept. |
| `*device-info-vid*` | Version ID (firmware version tag). |
| `*device-info-sdk-version*` | SDK version string written into cfg at generation time. |
| `*device-info-checksum*` | Checksum of the saved config, validated on load. |

> These fields are typically auto-populated when you click Save. You should not manually edit them.  
> Mismatch between PID in `cfg_tool.bin` and `isd_config.ini` can cause the device to reject OTA updates.

---

## Top Toolbar Buttons

| Button | Action |
|--------|--------|
| **Upgrade** (top right) | Online upgrade path — pushes current config to connected device via SPP/USB/UART if `TCFG_CFG_TOOL_ENABLE = ENABLE` |
| **Save** (top right) | Writes current GUI state to `cfg_tool.bin`. This is the offline path. Always use this before building firmware. |

---

## Complete Workflow Summary

```
1. Open jlxproj → Config Tool button
2. Set BT Config: BT Name slot 1, EDR MAC, BLE MAC
3. Set Common Config: tones, LEDs, shutdown timer
4. Set Call Config: AEC/NS/AGC/NLP as needed
5. Set Volume Config: choose MeanStep or FixedStep, Generate, verify output
6. Set Tone File Config: assign .wts files to event slots
7. Set ANC Config: gains and topology for your ANC hardware
8. Click SAVE (top right)
9. Rebuild firmware (.vscode/winmk.bat all)
10. Flash using download_app_ota_identity_clean.bat for first flash / identity update
    OR normal download_app_ota.bat for firmware-only updates
11. Forget old BT pairing on phone, rescan
```

---

## Generated File Locations

| File | Path | Tab that generates it |
|------|----- |----------------------|
| `cfg_tool.bin` | `cpu/br28/tools/cfg_tool.bin` | All tabs via Save |
| `tone.cfg` | `cpu/br28/tools/tone.cfg` | Tone File Config |
| `eq_cfg_hw.bin` | `cpu/br28/tools/eq_cfg_hw.bin` | (Audio Effect Tool, separate button) |
| `anc_coeff.bin` | `cpu/br28/tools/anc_coeff.bin` | (ANC Designer, separate button) |
| `anc_gains.bin` | `cpu/br28/tools/anc_gains.bin` | ANC Config gains |

---

## Firmware Read Path (How cfg_tool.bin values reach the code)

```
cfg_tool.bin (flash)
    ↓ syscfg_read(CFG_ID, buf, len)
    ↓ 
user_cfg.c: cfg_file_parse()
    ├── CFG_BT_NAME      → bt_cfg.edr_name
    ├── CFG_BLE_NAME     → bt_cfg.ble_name
    ├── CFG_BT_MAC_ADDR  → bt_cfg.mac_addr
    ├── CFG_BLE_MAC_ADDR → le_controller_set_mac() [FIX-005]
    ├── CFG_BT_RF_POWER_ID → bt_max_pwr_set()
    ├── CFG_AEC_ID       → CVP/AEC parameters
    └── CFG_SYS_VOL_ID   → volume table for DAC

earphone.c: BLE init
    └── CFG_BLE_MAC_ADDR → le_controller_set_mac() [FIX-005]
```
