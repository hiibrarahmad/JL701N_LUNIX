# BT_CONFIG - Bluetooth Configuration Structure

## Overview

The `BT_CONFIG` structure is the core Bluetooth configuration container for the JL7016G earphone firmware. It holds all essential Bluetooth parameters including device identity, audio gains, power settings, and TWS (True Wireless Stereo) pairing identifiers. This structure is initialized at boot time via **cfg_file_parse()** in `user_cfg.c` and persists data across power cycles using the **syscfg (System Configuration)** layer.

---

## Structure Definition

**File:** `include_lib/system/user_cfg.h`

```c
typedef struct __BT_CONFIG {
    u8 edr_name[LOCAL_NAME_LEN];       // Classic Bluetooth device name (32 bytes)
    u8 mac_addr[6];                    // Bluetooth EDR MAC address (6 bytes)
    u8 rf_power;                       // TX power (0-10 = -20 dBm to +9 dBm)
    u8 dac_analog_gain;                // Call DAC analog gain (0-30 typical)
    u8 mic_analog_gain;                // Call MIC gain (0-15 typical)
    u16 tws_device_indicate;           // TWS pair discovery identifier (0x0000-0xFFFF)
    u8 tws_local_addr[6];              // TWS local device address (6 bytes)
    u8 ble_name[LOCAL_NAME_LEN];       // BLE device name (32 bytes, optional)
    u8 ble_mac_addr[6];                // BLE MAC address (6 bytes)
    u8 ble_rf_power;                   // BLE TX power (0-9 dBm scale)
} _GNU_PACKED_ BT_CONFIG;
```

**Constant:** `LOCAL_NAME_LEN = 32` bytes

---

## Default Instance in user_cfg.c

```c
BT_CONFIG bt_cfg = {
    .edr_name        = {'Y', 'L', '-', 'B', 'R', '3', '0'},
    .mac_addr        = {0xff, 0xff, 0xff, 0xff, 0xff, 0xff},
    .tws_local_addr  = {0xff, 0xff, 0xff, 0xff, 0xff, 0xff},
    .rf_power        = 10,
    .dac_analog_gain = 25,
    .mic_analog_gain = 7,
    .tws_device_indicate = 0x6688,
};
```

---

## Detailed Parameter Explanation

### 1. **edr_name** (Bluetooth Device Name)

| Property | Value |
|----------|-------|
| **Type** | `u8[32]` character array |
| **Length** | Up to 32 bytes (null-terminated display string) |
| **Syscfg ID** | `CFG_BT_NAME (101)` |
| **Scope** | Classic Bluetooth (EDR) advertisement name |
| **Default Value** | `"YL-BR30"` (7 characters) |

**Function:** Specifies the human-readable name displayed during Bluetooth device discovery. This is what users see when scanning for available Bluetooth devices on their phone or another device.

**Usage:**
- Sent in Bluetooth scan response packets (HCI command: HCI_Write_Local_Name)
- Maximum 31 printable characters (32nd byte typically '\0' for null termination)
- Can be dynamically changed at runtime via `bt_modify_name()`

**Related Code:**
```c
const char *bt_get_local_name() {
    return (const char *)(bt_cfg.edr_name);
}

extern void lmp_hci_write_local_name(const char *name);
int bt_modify_name(u8 *new_name) { ... }
```

**Example Values:**
- `"YL-BR30"` — Product model designation
- `"JL7016G-L"` — Chipset + orientation (Left)
- `"earbuds-pro"` — User-friendly name

---

### 2. **mac_addr** (Bluetooth MAC Address)

| Property | Value |
|----------|-------|
| **Type** | `u8[6]` byte array |
| **Format** | 48-bit IEEE 802.11 MAC address |
| **Syscfg ID** | `CFG_BT_MAC_ADDR (102)` |
| **Scope** | EDR (Classic Bluetooth) link layer identity |
| **Default Value** | `0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF` (triggers random generation at boot) |
| **Storage** | BTIF region (persistent VM) |

**Function:** Unique Bluetooth MAC address for the earphone in EDR mode. This identifies the device at the link layer during connection and pairing.

**Address Format (6 bytes, Big-Endian display):**
- Bytes 0-2: **OUI (Organizationally Unique Identifier)** — manufacturer code
- Bytes 3-5: **Device Unique ID** — assigned per unit

**Example:** `3C:00:0A:7E:1A:00`
```
3C:00:0A = Jieli company OUI (3C00 0A in manufacturer database)
7E:1A:00 = Unit-specific ID (assigned during provisioning)
```

**Initialization Logic (from user_cfg.c):**

```c
u8 mac_buf[6];
u8 mac_buf_tmp[6] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

ret = syscfg_read(CFG_BT_MAC_ADDR, mac_buf, 6);
if ((ret != 6) || !memcmp(mac_buf, mac_buf_tmp, 6) || !memcmp(mac_buf, mac_buf_tmp2, 6)) {
    get_random_number(mac_buf, 6);          // Generate random address if not stored
    syscfg_write(CFG_BT_MAC_ADDR, mac_buf, 6);  // Persist to BTIF
}
memcpy(bt_cfg.mac_addr, mac_buf, 6);
```

**Boot Behavior:**
1. Attempt to read MAC from BTIF (persistent storage)
2. If not stored (all 0xFF or all 0x00), generate random address
3. Persist the generated/stored address back to BTIF
4. Copy to runtime `bt_cfg.mac_addr`

**TWS Provisioning Context:**
In TWS mode, each earbud gets a **unique MAC address**:
- **Left Earbud (L):** Base MAC (even byte)
- **Right Earbud (R):** Base MAC + 1 (odd byte)
- **Sibling relationship:** Defined by `tws_local_addr` and `CFG_TWS_REMOTE_ADDR`

**For JL7016G Manual Provisioning:**
- Base: `3C:00:0A:7E:1A:00`
- Pair 1: L=`00`, R=`01` | Pair 2: L=`02`, R=`03` | ... Pair 5: L=`08`, R=`09`

---

### 3. **rf_power** (Transmit Power Level)

| Property | Value |
|----------|-------|
| **Type** | `u8` (0-10 scale) |
| **Syscfg ID** | `CFG_BT_RF_POWER_ID (601)` |
| **Range** | 0 → -20 dBm (minimum), 10 → +9 dBm (maximum) |
| **Default Value** | 10 (maximum power: +9 dBm) |
| **Hardware Support** | JL7016G (BR28) max output: +9 dBm |

**Function:** Controls the RF transmit power for Bluetooth EDR (Classic Bluetooth). Higher values increase range but consume more power. Lower values reduce power consumption but limit range.

**Power Mapping (Typical):**
```
rf_power = 0  → -20 dBm (minimum, ~1 mW)
rf_power = 5  → -5 dBm  (medium, ~316 µW)
rf_power = 10 → +9 dBm  (maximum, ~8 mW)
```

**Typical Use Cases:**
- **10 (Maximum):** Maximize range for TWS discovery and reconnection
- **8-9:** Balance range and battery life
- **5-6:** Low-power profile for connected mode (range ~5-10 meters)
- **0-3:** Ultra-low power (testing, special modes)

**Hardware Application:**
```c
// From cfg_file_parse() in user_cfg.c
ret = syscfg_read(CFG_BT_RF_POWER_ID, &app_var.rf_power, 1);
if (ret < 0) {
    app_var.rf_power = 10;  // Default to max
}
bt_max_pwr_set(app_var.rf_power, 5, 8, 9);  // BLE power: 9 dBm
```

**Note:** The **BLE TX power** is set separately in the last parameter (9 = max BLE power), independent of EDR power.

---

### 4. **dac_analog_gain** (Call DAC Analog Gain)

| Property | Value |
|----------|-------|
| **Type** | `u8` (typical 0-30 dB) |
| **Scope** | Speaker output level during voice calls |
| **Default Value** | 25 (dB) |
| **Hardware Integration** | JL7016G built-in DAC → Analog speaker driver |

**Function:** Controls the analog gain of the DAC (Digital-to-Analog Converter) output, which drives the speaker during phone calls. This is distinct from the digital volume control.

**Gain Scale (Typical):**
- 0 dB = Mute/Minimum
- 10 dB = ~3.2x voltage
- 20 dB = ~10x voltage
- 25 dB = ~17.8x voltage (default)
- 30 dB = Maximum (~31.6x voltage)

**Typical Values by Use Case:**
| Value | Use Case | Characteristics |
|-------|----------|-----------------|
| 15-18 | Call mode | Balanced volume for phone calls |
| 20-25 | Normal | Default for earphones |
| 25-30 | Loud environment | Maximized speaker output |

**Related Code:**
```c
// In audio_config.h or audio settings
#define SYS_DEFAULT_VOL         20
#define SYS_MAX_VOL             30

// Runtime configuration
app_var.aec_dac_gain = aec.dac_again;  // AEC-specific DAC gain
app_var.call_volume  = app_var.aec_dac_gain;  // Call uses DAC gain
```

**Distinction from Digital Volume:**
- **DAC Analog Gain** (this field): Analog amplification (fixes background noise floor)
- **Digital Volume** (`app_var.music_volume`): Digital attenuation (0-127 or 0-15 scale)
- Typical flow: Digital Volume → DAC → Speaker

---

### 5. **mic_analog_gain** (Call MIC Analog Gain)

| Property | Value |
|----------|-------|
| **Type** | `u8` (typical 0-15 dB) |
| **Scope** | Microphone input preamplifier gain |
| **Default Value** | 7 (dB) |
| **Hardware Integration** | JL7016G built-in mic preamp → ADC |

**Function:** Controls the analog gain of the microphone preamplifier, affecting the input signal level to the ADC before digital processing (AEC, noise cancellation, etc.).

**Gain Scale (Typical):**
- 0 dB = Minimum (low SNR, quiet but low noise)
- 7 dB = Default (~2.2x voltage)
- 12 dB = Medium (~4x voltage)
- 15 dB = Maximum (~5.6x voltage, high gain but risk of saturation)

**Typical Values by Microphone Type:**
| Mic Type | Recommended Gain | Rationale |
|----------|------------------|-----------|
| MEMS (High Sensitivity) | 0-5 dB | Already good SNR, avoid saturation |
| Electret (Medium Sensitivity) | 5-10 dB | Balanced input level |
| Passive (Low Sensitivity) | 12-15 dB | Maximize weak signal |

**Related Code:**
```c
// AEC configuration reads from syscfg
AEC_CONFIG aec;
ret = syscfg_read(CFG_AEC_ID, &aec, sizeof(aec));
if (ret == sizeof(aec)) {
    app_var.aec_mic_gain = aec.mic_again;   // Assigned from AEC config
    app_var.aec_mic1_gain = aec.mic_again;
    ...
}
```

**Impact on Audio Quality:**
- **Too Low (<3 dB):** Weak input signal → background noise amplified during call → poor intelligibility
- **Just Right (5-10 dB):** Clean voice capture with minimal distortion
- **Too High (>15 dB):** Saturation/clipping → distorted mic audio, feedback loops

---

### 6. **tws_device_indicate** (TWS Pair Discovery Code)

| Property | Value |
|----------|-------|
| **Type** | `u16` (16-bit unsigned integer) |
| **Syscfg ID** | `CFG_TWS_PAIR_CODE_ID (602)` |
| **Format** | Big-Endian unsigned word |
| **Default Value** | `0x6688` (in default instance) |
| **Range** | 0x0000 - 0xFFFF (65536 possible values) |

**Function:** A **pairing marker** used during TWS device discovery (inquiry and page). When two buds search for each other, they only connect if their `tws_device_indicate` values match. This prevents cross-pair mixing and accidental connections.

**Mechanism:**
1. Bud A (Left) sends inquiry with `tws_device_indicate = 0x6688`
2. Bud B (Right) receives inquiry, checks if `tws_device_indicate` matches
3. **If match:** Bud B responds and pairing proceeds
4. **If no match:** Bud B ignores inquiry (cross-pair isolation maintained)

**Usage in Code:**
```c
// From user_cfg.c - cfg_file_parse()
ret = syscfg_read(CFG_TWS_PAIR_CODE_ID, &bt_cfg.tws_device_indicate, 2);
if (ret < 0) {
    log_debug("read pair code err");
    bt_cfg.tws_device_indicate = 0x8888;  // Fallback
}
log_info("tws pair code config:");
log_info_hexdump(&bt_cfg.tws_device_indicate, 2);
```

**Multi-Pair Deployment Strategy:**
To manage multiple pairs without cross-interference, assign **unique pair codes** to each pair:

| Pair | Left Bud | Right Bud | Pair Code | Rationale |
|------|----------|-----------|-----------|-----------|
| Pair 1 (Dev Kit) | B01 | B02 | 0x6688 | Default development |
| Pair 2 (QA Test) | B03 | B04 | 0x6699 | Isolated QA env |
| Pair 3 (Production) | B05 | B06 | 0x66AA | Factory build |
| Pair 4 (Reserved) | B07 | B08 | 0x66BB | Future use |
| Pair 5 (Reserved) | B09 | B10 | 0x66CC | Future use |

**Factory Provisioning Workflow:**
- **Step 1:** Assign unique pair code to firmware build
- **Step 2:** Flash same pair code to both L and R buds of a pair
- **Step 3:** Test pairing occurs only within pair
- **Step 4:** Verify no cross-pair connections occur

---

### 7. **tws_local_addr** (TWS Local Address / Device Orientation)

| Property          | Value                                                            |
| ----------------- | ---------------------------------------------------------------- |
| **Type**          | `u8[6]` (6 bytes)                                                |
| **Syscfg ID**     | `CFG_TWS_LOCAL_ADDR (95)`                                        |
| **Format**        | Bluetooth MAC address                                            |
| **Scope**         | TWS device identity (separate from EDR MAC)                      |
| **Relationship**  | Links to `CFG_TWS_REMOTE_ADDR` (sibling's address)               |
| **Default Value** | `0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF` (auto-generated if not set) |

**Function:** Stores the **local TWS identity address** for a single bud, independent of the EDR MAC address. This allows TWS synchronization and sibling discovery without conflicting with classic Bluetooth addressing.

**Initialization (from user_cfg.c):**
```c
#if TCFG_USER_TWS_ENABLE
    int len = syscfg_read(CFG_TWS_LOCAL_ADDR, bt_cfg.tws_local_addr, 6);
    if (len != 6) {
        get_random_number(bt_cfg.tws_local_addr, 6);  // Generate random if not stored
        syscfg_write(CFG_TWS_LOCAL_ADDR, bt_cfg.tws_local_addr, 6);
    }
    log_debug("tws_local_mac:");
    log_info_hexdump(bt_cfg.tws_local_addr, sizeof(bt_cfg.tws_local_addr));
#endif
```

**Multi-Layer Identity Model for JL7016G:**

Each bud maintains **3 independent MAC addresses**:

| Address Type   | Syscfg ID | Purpose                                   | Example             |
| -------------- | --------- | ----------------------------------------- | ------------------- |
| **EDR MAC**    | 102       | Classic Bluetooth identity (host sees)    | `3C:00:0A:7E:1A:00` |
| **TWS Local**  | 95        | Intra-TWS pairing (L-R synchronization)   | `AA:BB:CC:DD:EE:00` |
| **TWS Remote** | 96        | Sibling bud reference (link to pair)      | `AA:BB:CC:DD:EE:01` |
| **TWS Common** | 97        | Pair-level identity (shared by both buds) | `AA:BB:CC:DD:EE:FF` |

**Provisioning Example (Pair 1):**

**Left Bud (B01):**
```
CFG_BT_MAC_ADDR (102)       = 3C:00:0A:7E:1A:00  (EDR)
CFG_TWS_LOCAL_ADDR (95)     = AA:BB:CC:DD:EE:00  (TWS Local)
CFG_TWS_REMOTE_ADDR (96)    = AA:BB:CC:DD:EE:01  (Sibling = Right)
CFG_TWS_COMMON_ADDR (97)    = AA:BB:CC:DD:EE:FF  (Pair Identity)
```

**Right Bud (B02):**
```
CFG_BT_MAC_ADDR (102)       = 3C:00:0A:7E:1A:01  (EDR)
CFG_TWS_LOCAL_ADDR (95)     = AA:BB:CC:DD:EE:01  (TWS Local)
CFG_TWS_REMOTE_ADDR (96)    = AA:BB:CC:DD:EE:00  (Sibling = Left)
CFG_TWS_COMMON_ADDR (97)    = AA:BB:CC:DD:EE:FF  (Pair Identity)
```

**Key Property:** `tws_local_addr` on **Left** must equal `CFG_TWS_REMOTE_ADDR` on **Right**, and vice versa (reciprocal sibling relationship).

---

### 8. **ble_name** (BLE Device Name)

| Property | Value |
|----------|-------|
| **Type** | `u8[32]` character array |
| **Length** | Up to 32 bytes |
| **Syscfg ID** | `CFG_BLE_NAME (103)` |
| **Scope** | BLE advertisement name |
| **Default Behavior** | Falls back to `edr_name` if not set |

**Function:** Specifies the device name for Bluetooth Low Energy (BLE) advertisements. Used when the device operates in BLE mode (e.g., for companion apps or firmware updates).

**Related Code:**
```c
const char *bt_get_ble_local_name() {
    if (bt_cfg.ble_name[0]) {
        return (const char *)(bt_cfg.ble_name);
    }
    return bt_get_local_name();  // Fallback to EDR name
}
```

**Typical Values:**
- If set: `"YL-BR30-BLE"` (explicit BLE branding)
- If empty: Falls back to `edr_name` (`"YL-BR30"`)

---

### 9. **ble_mac_addr** (BLE MAC Address)

| Property | Value |
|----------|-------|
| **Type** | `u8[6]` byte array |
| **Syscfg ID** | `CFG_BLE_MAC_ADDR (104)` |
| **Format** | Bluetooth LE address (static random or public) |
| **Scope** | BLE-only link layer identity |

**Function:** Separate MAC address used **only for BLE communications** (GAP/GATT profiles). Independent from EDR MAC to allow simultaneous EDR and BLE operation on dual-mode chips like BR28.

**Typical Scenario:**
- **EDR MAC** (`mac_addr`): Used for classic Bluetooth phone connections
- **BLE MAC** (`ble_mac_addr`): Used for companion app / firmware update server connections
- **Can operate simultaneously:** Phone connected via EDR, app connected via BLE

---

### 10. **ble_rf_power** (BLE Transmit Power)

| Property | Value |
|----------|-------|
| **Type** | `u8` (0-9 scale) |
| **Range** | 0 → -20 dBm to 9 → +9 dBm (or regional limit) |
| **Default** | Typically 9 (maximum) |
| **Scope** | BLE-only TX power |

**Function:** Independent TX power control for BLE advertisements and connections. Does not affect EDR TX power (`rf_power`).

**Typical Values:**
- **9:** Maximum BLE power (+9 dBm) — maximize discovery range
- **5:** Medium power (-5 dBm) — balance range and battery
- **1:** Low power (-19 dBm) — ultra-low energy mode

---

## Initialization Flow

```
Boot → cfg_file_parse() 
    ├─ Read CFG_BT_NAME → edr_name
    ├─ Read CFG_BT_RF_POWER_ID → rf_power
    ├─ Read CFG_TWS_PAIR_CODE_ID → tws_device_indicate
    ├─ Read CFG_AEC_ID → dac_analog_gain, mic_analog_gain
    ├─ Read CFG_BT_MAC_ADDR → mac_addr (or generate random)
    ├─ Read CFG_TWS_LOCAL_ADDR → tws_local_addr (or generate random)
    └─ Read CFG_BLE_NAME → ble_name (optional)
    
    ↓
    bt_cfg populated ← used for entire runtime
```

---

## Persistence & Storage

**Two Storage Regions:**

| Config | Region | ID | Persistent | Accessible | Notes |
|--------|--------|----|----|----|----|
| mac_addr, ble_mac_addr, RF power | **BTIF** (64-512 B) | 102, 104, 601 | ✅ Yes | HCI controller | Persists across power cycles |
| edr_name, tws_pair_code | **VM** (large) | 101, 602 | ✅ Yes | Software only | Read during cfg_file_parse() |
| tws_local_addr, tws_remote_addr | **VM** | 95, 96 | ✅ Yes | Sibling lookup | Synchronization between pair |

**Write Path:**
```c
syscfg_write(CFG_BT_MAC_ADDR, mac_buf, 6);  // Persist to BTIF
syscfg_write(CFG_TWS_LOCAL_ADDR, addr, 6);  // Persist to VM
```

---

## Practical Configuration Table (Multi-Pair Factory Deployment)

**For 5 Pairs of JL7016G Earphones:**

| Pair | Bud | EDR MAC | TWS Local | TWS Remote | Pair Code | edr_name |
|------|-----|---------|-----------|------------|-----------|----------|
| **P1** | L | 3C:00:0A:7E:1A:00 | AA:BB:CC:00:01:00 | AA:BB:CC:00:01:01 | 0x6688 | YL-BR30-P1L |
|  | R | 3C:00:0A:7E:1A:01 | AA:BB:CC:00:01:01 | AA:BB:CC:00:01:00 | 0x6688 |  YL-BR30-P1R |
| **P2** | L | 3C:00:0A:7E:1A:02 | AA:BB:CC:00:02:00 | AA:BB:CC:00:02:01 | 0x6699 | YL-BR30-P2L |
|  | R | 3C:00:0A:7E:1A:03 | AA:BB:CC:00:02:01 | AA:BB:CC:00:02:00 | 0x6699 | YL-BR30-P2R |
| **P3** | L | 3C:00:0A:7E:1A:04 | AA:BB:CC:00:03:00 | AA:BB:CC:00:03:01 | 0x66AA | YL-BR30-P3L |
|  | R | 3C:00:0A:7E:1A:05 | AA:BB:CC:00:03:01 | AA:BB:CC:00:03:00 | 0x66AA | YL-BR30-P3R |
| **P4** | L | 3C:00:0A:7E:1A:06 | AA:BB:CC:00:04:00 | AA:BB:CC:00:04:01 | 0x66BB | YL-BR30-P4L |
|  | R | 3C:00:0A:7E:1A:07 | AA:BB:CC:00:04:01 | AA:BB:CC:00:04:00 | 0x66BB | YL-BR30-P4R |
| **P5** | L | 3C:00:0A:7E:1A:08 | AA:BB:CC:00:05:00 | AA:BB:CC:00:05:01 | 0x66CC | YL-BR30-P5L |
|  | R | 3C:00:0A:7E:1A:09 | AA:BB:CC:00:05:01 | AA:BB:CC:00:05:00 | 0x66CC | YL-BR30-P5R |

**Other Parameters (Same for All Pairs):**
- `rf_power`: 10 (max power)
- `dac_analog_gain`: 25 dB
- `mic_analog_gain`: 7 dB
- `ble_rf_power`: 9 (max BLE power)

---

## Key Takeaways

1. **BT_CONFIG is the runtime Bluetooth configuration hub** — loaded from persistent storage at boot
2. **Multiple identity layers** — EDR MAC, TWS Local, TWS Remote, BLE MAC for different link purposes
3. **Power settings** — `rf_power` and `ble_rf_power` independent (EDR vs BLE)
4. **Audio gains** — `dac_analog_gain` (speaker) and `mic_analog_gain` (mic) critical for call quality
5. **TWS pairing** — `tws_device_indicate` (pair code) and reciprocal `tws_local_addr`/`tws_remote_addr` prevent cross-pair interference
6. **Factory provisioning** — Manual assignment of all MAC addresses and pair codes required for multi-pair deployment
7. **No auto-derivation** — Each bud receives explicit identity values (no algorithmic sibling calculation)

---

## Related Files & Functions

- **Definition:** `include_lib/system/user_cfg.h`
- **Initialization:** `apps/earphone/user_cfg.c` → `cfg_file_parse()`
- **Syscfg IDs:** `include_lib/system/syscfg_id.h`
- **Getter Functions:**
  - `bt_get_mac_addr()` → `mac_addr`
  - `bt_get_local_name()` → `edr_name`
  - `bt_get_ble_local_name()` → `ble_name` (with fallback)
  - `bt_get_tws_local_addr()` → `tws_local_addr`
  - `bt_get_tws_device_indicate()` → `tws_device_indicate`

---

## Cross-References

- [MAC ADDRESS PROVISIONING](../MAC%20ADDRESS%20PROVISIONING/00%20-%20MAC%20ADDRESS%20PROVISIONING%20INDEX.md) — Detailed multi-pair MAC planning
- [DATASHEET COMPARISON - AC6966B vs JL7016G](../MIGRATION%20COMPARISON/DATASHEET%20COMPARISON%20-%20AC6966B%20vs%20JL7016G%20(Hardware%2C%20BLE%20Antenna%2C%20Robustness).md) — Hardware RF specifications
- [POWER PRIORITY 01 — LDO vs Buck DC-DC](POWER%20PRIORITY%2001%20%E2%80%94%20LDO%20vs%20Buck%20DC-DC%20on%20JL7016G%20Hybrid.md) — Power management considerations

---

## Related FIX Records

| Fix | Title | Relevance |
|-----|-------|-----------|
| [FIX-005](../../FIXING/FIX-005%20—%20BLE%20MAC%20Address%20Ignored%20at%20Boot.md) | BLE MAC address ignored at boot | BT MAC provisioning |
| [FIX-006](../../FIXING/FIX-006%20—%20Hardcoded%20Buddie%20Name%20Overwrites%20Config%20GUI%20Name.md) | Hardcoded name overwrites Config GUI | BT device name config |

