---
tags: [tws, pairing, sibling, storage, firmware, homework, mac-address]
status: in-progress
created: 2026-05-19
---

# TWS Pairing & Sibling Store Records - Deep Dive Homework

## Executive Summary
When TWS pairing happens for the **first time**, both earbuds must store:
1. Each other's MAC address (CFG_TWS_REMOTE_ADDR) = 6 bytes
2. Shared pairing identity (CFG_TWS_COMMON_ADDR) = 6 bytes  
3. Local channel assignment (CFG_TWS_CHANNEL) = 1 byte (L/R/U)

This enables reconnection without re-pairing.

---

## Storage Architecture

### Per-Bud Configuration IDs (syscfg)
| Config ID | Purpose | Size | Default | Initial State |
|-----------|---------|------|---------|---|
| **95** | CFG_TWS_LOCAL_ADDR | 6B | {0xFF,0xFF,0xFF,0xFF,0xFF,0xFF} | Own random MAC on first boot |
| **97** | CFG_TWS_COMMON_ADDR | 6B | {0xFF,0xFF,0xFF,0xFF,0xFF,0xFF} | Derived from pair (shared by both) |
| **98** | CFG_TWS_REMOTE_ADDR | 6B | {0xFF,0xFF,0xFF,0xFF,0xFF,0xFF} | Sibling's MAC (different per bud) |
| **99** | CFG_TWS_CHANNEL | 1B | 'U' (unknown) | 'L' or 'R' after pair |
| **602** | CFG_TWS_PAIR_CODE_ID | 2B | 0x6688 | Discovery code (same for both) |

---

## First-Time Pairing Flow

### Phase 1: Boot & Configuration Read
**Location:** `apps/earphone/user_cfg.c` lines 555-568

```c
int len = syscfg_read(CFG_TWS_LOCAL_ADDR, bt_cfg.tws_local_addr, 6);
if (len != 6) {
    get_random_number(bt_cfg.tws_local_addr, 6);  // Generate random if first boot
    syscfg_write(CFG_TWS_LOCAL_ADDR, bt_cfg.tws_local_addr, 6);
}

u8 tws_common_addr[6] = {0};
ret = syscfg_read(CFG_TWS_COMMON_ADDR, tws_common_addr, 6);
if (ret == 6) {
    // Already paired before, use stored common addr
    log_debug("tws_common_mac:");
    log_info_hexdump(tws_common_addr, sizeof(tws_common_addr));
}
```

**Result:**
- LEFT bud generates: `[L_MAC0, L_MAC1, L_MAC2, L_MAC3, L_MAC4, L_MAC5]`
- RIGHT bud generates: `[R_MAC0, R_MAC1, R_MAC2, R_MAC3, R_MAC4, R_MAC5]`
- Each stores in CFG_TWS_LOCAL_ADDR

---

### Phase 2: Power-On & Sibling Detection
**Location:** `apps/earphone/bt_tws.c` lines 930-1010

```c
err = tws_get_sibling_addr(addr, &result);  // Try to read CFG_TWS_REMOTE_ADDR
if (err == 0) {
    // ========== ALREADY PAIRED (reconnect path) ==========
    gtws.state |= BT_TWS_PAIRED;
    EARPHONE_STATE_TWS_INIT(1);  // Already paired
    tws_api_set_sibling_addr(addr);  // Tell BT controller sibling's MAC
    bt_tws_connect_sibling(CONFIG_TWS_CONNECT_SIBLING_TIMEOUT);
} else {
    // ========== FIRST TIME / UNPAIRED (new pairing path) ==========
    gtws.state |= BT_TWS_UNPAIRED;
    EARPHONE_STATE_TWS_INIT(0);  // Not paired yet
    tws_auto_pair_enable = 1;  // Enable automatic pairing search
    bt_tws_connect_sibling(6);  // Start searching for sibling
}
```

**Decision Point:**
```
Does CFG_TWS_REMOTE_ADDR contain valid sibling MAC?
  ├─ YES (all bytes != 0xFF)  → PAIRED state → goto Reconnection
  └─ NO  (all bytes == 0xFF)  → UNPAIRED state → goto New Pairing
```

---

### Phase 3: Pairing Discovery & Connection
**Location:** `apps/earphone/bt_tws.c` lines 282-287 (auto pair code generation)

```c
u8 *tws_set_auto_pair_code(void)
{
    u8 auto_pair_code[6] = {0x34, 0x66, 0x33, 0x87, 0x09, 0x42};
    u16 code = bt_get_tws_device_indicate();  // Read CFG_TWS_PAIR_CODE_ID (0x6688)
    auto_pair_code[0] = code >> 8;   // 0x66
    auto_pair_code[1] = code & 0xff; // 0x88
    return auto_pair_code;
}
```

**Pairing Code: `0x66, 0x88, 0x33, 0x87, 0x09, 0x42`**  
Both buds advertise/scan with this code, allowing discovery.

---

### Phase 4: TWS Connection Established → STORE SIBLING MAC
**Location:** `apps/earphone/bt_tws.c` lines 1492-1535 (TWS_EVENT_CONNECTED handler)

**THIS IS THE CRITICAL SECTION where sibling MAC is FIRST RECORDED:**

```c
case TWS_EVENT_CONNECTED:
    // Read what's currently stored
    syscfg_read(CFG_TWS_REMOTE_ADDR, addr[0], 6);   // [What was stored before]
    syscfg_read(CFG_TWS_COMMON_ADDR, addr[1], 6);   // [Shared pair ID]
    tws_api_get_sibling_addr(addr[2]);              // [What we're connected to NOW]
    tws_api_get_local_addr(addr[3]);                // [Our address NOW]

    // ====== FIRST PAIRING: Store sibling's MAC ======
    if (memcmp(addr[0], addr[2], 6)) {
        // Sibling MAC changed (or first time)
        syscfg_write(CFG_TWS_REMOTE_ADDR, addr[2], 6);  // ← SAVE SIBLING MAC
        pair_suss = 1;
        log_info("rec tws addr\n");
    }

    // ====== FIRST PAIRING: Store common pair address ======
    if (memcmp(addr[1], addr[3], 6)) {
        // Common address changed (or first time)
        syscfg_write(CFG_TWS_COMMON_ADDR, addr[3], 6);  // ← SAVE PAIR IDENTITY
        pair_suss = 1;
        log_info("rec comm addr\n");
    }

    if (pair_suss) {
        gtws.state = BT_TWS_PAIRED;
        bt_update_mac_addr((void *)addr[3]);  // Update BT MAC address
    }

    // ====== ALSO STORE CHANNEL ======
    channel = tws_api_get_local_channel();
    if (channel != bt_tws_get_local_channel()) {
        syscfg_write(CFG_TWS_CHANNEL, &channel, 1);  // ← SAVE 'L' or 'R'
    }
    
    EARPHONE_STATE_TWS_CONNECTED(pair_suss, addr[3]);
    break;
```

**After First Pairing:**
- LEFT bud stores:
  - CFG_TWS_LOCAL_ADDR = `[L_MAC0...L_MAC5]` (own)
  - CFG_TWS_REMOTE_ADDR = `[R_MAC0...R_MAC5]` (sibling RIGHT)
  - CFG_TWS_COMMON_ADDR = `[L_MAC0+R_MAC0, L_MAC1+R_MAC1, ...]` (pair sum)
  - CFG_TWS_CHANNEL = 'L'

- RIGHT bud stores:
  - CFG_TWS_LOCAL_ADDR = `[R_MAC0...R_MAC5]` (own)
  - CFG_TWS_REMOTE_ADDR = `[L_MAC0...L_MAC5]` (sibling LEFT)
  - CFG_TWS_COMMON_ADDR = `[L_MAC0+R_MAC0, L_MAC1+R_MAC1, ...]` (pair sum, **same**)
  - CFG_TWS_CHANNEL = 'R'

---

## Reconnection Flow (After Pairing Stored)

### Boot Sequence
```
Boot → Read CFG_TWS_REMOTE_ADDR
  ├─ Valid MAC (not 0xFF) → PAIRED state
  │   └─ Call tws_api_set_sibling_addr(stored_sibling_mac)
  │   └─ Connect to stored MAC directly
  └─ All 0xFF → UNPAIRED state
      └─ Start pairing discovery
```

---

## Hardware: PC5 Pull-Up/Pull-Down Impact

From configuration [apps/earphone/board/br28/board_jl7018f_demo_cfg.h](apps/earphone/board/br28/board_jl7018f_demo_cfg.h#L1029):

```c
#define TCFG_LINEIN_CHECK_PORT              IO_PORTC_05     // Uses PC5
#define TCFG_LINEIN_AD_CHANNEL              AD_CH_PC5
#define TCFG_LINEIN_PORT_IN_DET_VOLTAGE     2800  // Pull-up detection
#define TCFG_LINEIN_PORT_OUT_DET_VOLTAGE    2600  // Pull-down detection
```

**PC5 Role:** Analog line-in detection (not directly TWS pairing)

**But Impact on TWS Reconnect:**
- If PC5 floats (no pull-up/down), analog reads become unstable
- Unstable ADC → possible false aux/linein detection
- False detection → interrupt TWS reconnect flow
- **Result:** Sibling stored but reconnection fails without PC5 bias

**Verify PC5 Config:**
- Check if resistor network exists on PCB schematic for PC5
- Confirm TCFG_LINEIN_ENABLE is set correctly
- If using PC5 for other purposes, conflict could affect TWS

---

## Configuration for TWS Common Address

From `apps/earphone/include/app_config.h` line 216:

```c
#define CONFIG_TWS_COMMON_ADDR_SELECT       CONFIG_TWS_COMMON_ADDR_USED_LEFT
```

**Options:**
- `CONFIG_TWS_COMMON_ADDR_AUTO` (0) = generate random for pair identity
- `CONFIG_TWS_COMMON_ADDR_USED_LEFT` (1) = use LEFT bud's MAC as pair identity

**Current:** LEFT bud's MAC is used as the TWS pair address.

---

## First-Time Pairing: Expected Log Sequence

```
[Boot] tws_local_mac: 3C:00:0A:7E:1A:00  (LEFT bud)
[Boot] tws_common_mac: (not read, will be generated)
[Pairing Search] ... scanning for sibling ...
[Found] TWS_EVENT_CONNECTED
[Store] rec tws addr   → CFG_TWS_REMOTE_ADDR written with RIGHT bud MAC
[Store] rec comm addr  → CFG_TWS_COMMON_ADDR written with pair identity
[Success] gtws.state = BT_TWS_PAIRED
```

---

## Troubleshooting Checklist

### Symptom: First Pairing Works, But Can't Reconnect

**Check:**
1. ✓ Both buds show `[rec tws addr]` and `[rec comm addr]` after pairing
2. ✓ CFG_TWS_REMOTE_ADDR is not all 0xFF after pairing (use chargestore debug)
3. ✓ PC5 has stable voltage (pull-up or pull-down resistor confirmed)
4. ✓ CFG_TWS_CHANNEL is saved as 'L' or 'R', not 'U'

### Symptom: PC5 Pull Removed, Reconnect Fails

**Check:**
1. ✓ TCFG_LINEIN_ENABLE status
2. ✓ ADC channels not conflicting
3. ✓ PC5 schematic connection
4. ✓ If disabling linein, ensure no other device uses PC5

### Symptom: Sibling Address Shows 0xFF After Pairing

**Possible Causes:**
1. CFG storage write permission issue
2. Pairing succeeded but TWS_EVENT_CONNECTED not triggered
3. memcmp(addr[0], addr[2], 6) returning 0 (no change detected, so not written)
4. syscfg_write() failed silently

---

## Configuration Files Involved

| File | Purpose | Current |
|------|---------|---------|
| [apps/earphone/user_cfg.c](apps/earphone/user_cfg.c#L556) | Boot read/write CFG_TWS_LOCAL_ADDR | ✓ |
| [apps/earphone/bt_tws.c](apps/earphone/bt_tws.c#L1502) | Pairing store sibling & pair ID | ✓ |
| [apps/earphone/power_manage/app_chargestore.c](apps/earphone/power_manage/app_chargestore.c#L102) | Chargestore write CFG_TWS_* | ✓ |
| [apps/earphone/board/br28/board_jl7018f_demo_cfg.h](apps/earphone/board/br28/board_jl7018f_demo_cfg.h#L1029) | PC5 linein config | TCFG_LINEIN_ENABLE=? |
| [apps/earphone/include/app_config.h](apps/earphone/include/app_config.h#L216) | TWS common addr mode | CONFIG_TWS_COMMON_ADDR_USED_LEFT |

---

## Next Steps for Verification

1. **Log first pairing fully** to confirm both `rec tws addr` and `rec comm addr` appear
2. **Check chargestore dump** post-pairing to verify sibling MAC is non-0xFF
3. **Inspect PC5 circuit** on board schematic for pull-up/down components
4. **Test PC5 removal impact** in controlled step (add -> remove -> reconnect check)
5. **Compare LEFT/RIGHT logs** to ensure symmetric storage

---

**Status:** Initial analysis complete. Awaiting:
- Chargestore dump after first pairing
- PC5 circuit schematic review
- Reconnect failure logs with PC5 removed
