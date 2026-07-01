# MAC ADDRESS PROVISIONING - SDK Implementation Guide

## Overview

The JL7016G SDK has been updated with manual MAC provisioning functions. Two helper functions are now available in `apps/earphone/user_cfg.c`:

- `bt_provision_pair1_left_bud()` — Provisions Pair 1 Left bud (B01)
- `bt_provision_pair1_right_bud()` — Provisions Pair 1 Right bud (B02)

These functions write all required syscfg IDs to persistent storage during firmware initialization.

---

## How to Use

### Step 1: Enable Manual Provisioning in user_cfg.c

At the top of the provisioning section (after line ~520), you'll find:

```c
#define TCFG_MANUAL_MAC_PROVISIONING_ENABLE  1  // Set to 1 to enable
```

Keep this set to **1** to enable the provisioning code.

### Step 2: Uncomment the Desired Bud Configuration

In the `cfg_file_parse()` function around line ~540, find:

```c
#if TCFG_MANUAL_MAC_PROVISIONING_ENABLE
    // Uncomment the desired pair/bud configuration below
    // Only one should be active at a time per firmware image
    
    // bt_provision_pair1_left_bud();   // Pair 1, Left bud (B01)
    // bt_provision_pair1_right_bud();  // Pair 1, Right bud (B02)
#endif
```

**Uncomment ONE function per firmware build:**

#### For Left Bud (B01) firmware:
```c
    bt_provision_pair1_left_bud();   // Pair 1, Left bud (B01)
    // bt_provision_pair1_right_bud();
```

#### For Right Bud (B02) firmware:
```c
    // bt_provision_pair1_left_bud();
    bt_provision_pair1_right_bud();  // Pair 1, Right bud (B02)
```

### Step 3: Build Separate Firmware Images

Build two firmware images, one for each bud orientation:

```bash
# Terminal 1: Build Left Bud (B01) firmware
cd d:\jl7016g final approach\SDKS\FIRST PERIORITY SDK
.vscode/winmk.bat all
# Output: firmware_P1_LEFT.bin

# Terminal 2: Edit user_cfg.c to uncomment RIGHT bud function
# Then build Right Bud (B02) firmware
.vscode/winmk.bat all
# Output: firmware_P1_RIGHT.bin
```

### Step 4: Flash Each Bud

```bash
# Flash Left Bud (B01) with Pair 1 LEFT firmware
jlink_flash firmware_P1_LEFT.bin

# Flash Right Bud (B02) with Pair 1 RIGHT firmware
jlink_flash firmware_P1_RIGHT.bin
```

### Step 5: Verify Configuration

Once flashed, each bud will automatically provision and log:

**Left Bud (B01) Boot Log:**
```
[USER_CFG] Provisioning Pair 1 - LEFT BUD (B01)
[USER_CFG]   CFG_BT_MAC_ADDR (102) = 3C:00:0A:7E:1A:00
[USER_CFG]   CFG_TWS_LOCAL_ADDR (95) = 3C:00:0A:7E:1A:00
[USER_CFG]   CFG_TWS_REMOTE_ADDR (96) = 3C:00:0A:7E:1A:01 [sibling]
[USER_CFG]   CFG_TWS_COMMON_ADDR (97) = AA:BB:CC:00:01:FF [pair]
[USER_CFG]   CFG_TWS_CHANNEL (98) = 0x00 [LEFT]
[USER_CFG]   CFG_TWS_PAIR_CODE_ID (602) = 0x6688
```

**Right Bud (B02) Boot Log:**
```
[USER_CFG] Provisioning Pair 1 - RIGHT BUD (B02)
[USER_CFG]   CFG_BT_MAC_ADDR (102) = 3C:00:0A:7E:1A:01
[USER_CFG]   CFG_TWS_LOCAL_ADDR (95) = 3C:00:0A:7E:1A:01
[USER_CFG]   CFG_TWS_REMOTE_ADDR (96) = 3C:00:0A:7E:1A:00 [sibling]
[USER_CFG]   CFG_TWS_COMMON_ADDR (97) = AA:BB:CC:00:01:FF [pair]
[USER_CFG]   CFG_TWS_CHANNEL (98) = 0x01 [RIGHT]
[USER_CFG]   CFG_TWS_PAIR_CODE_ID (602) = 0x6688
```

---

## Adding Pairs 2-5 Configurations

The template functions show how to add more pairs. Follow this pattern for Pair 2-5:

### Pair 2 Example (P2):

Add these functions to `user_cfg.c` after the Pair 1 functions:

```c
// Pair 2 Configuration (P2)
void bt_provision_pair2_left_bud(void)
{
    u8 edr_mac[6]        = {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x02};  // EDR MAC
    u8 tws_local[6]      = {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x02};  // TWS Local
    u8 tws_remote[6]     = {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x03};  // Sibling (Right)
    u8 tws_common[6]     = {0xAA, 0xBB, 0xCC, 0x00, 0x02, 0xFF};  // Pair identity
    u8 tws_channel       = 0x00;                                   // Left
    u16 pair_code        = 0x6699;                                 // Pair 2 code

    log_info("Provisioning Pair 2 - LEFT BUD (B03)");
    syscfg_write(CFG_BT_MAC_ADDR, edr_mac, 6);
    syscfg_write(CFG_TWS_LOCAL_ADDR, tws_local, 6);
    syscfg_write(CFG_TWS_REMOTE_ADDR, tws_remote, 6);
    syscfg_write(CFG_TWS_COMMON_ADDR, tws_common, 6);
    syscfg_write(CFG_TWS_CHANNEL, &tws_channel, 1);
    syscfg_write(CFG_TWS_PAIR_CODE_ID, (u8 *)&pair_code, 2);
    log_info("  CFG_BT_MAC_ADDR = 3C:00:0A:7E:1A:02");
    log_info("  CFG_TWS_PAIR_CODE_ID = 0x6699");
}

void bt_provision_pair2_right_bud(void)
{
    u8 edr_mac[6]        = {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x03};  // EDR MAC
    u8 tws_local[6]      = {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x03};  // TWS Local
    u8 tws_remote[6]     = {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x02};  // Sibling (Left)
    u8 tws_common[6]     = {0xAA, 0xBB, 0xCC, 0x00, 0x02, 0xFF};  // Pair identity
    u8 tws_channel       = 0x01;                                   // Right
    u16 pair_code        = 0x6699;                                 // Pair 2 code

    log_info("Provisioning Pair 2 - RIGHT BUD (B04)");
    syscfg_write(CFG_BT_MAC_ADDR, edr_mac, 6);
    syscfg_write(CFG_TWS_LOCAL_ADDR, tws_local, 6);
    syscfg_write(CFG_TWS_REMOTE_ADDR, tws_remote, 6);
    syscfg_write(CFG_TWS_COMMON_ADDR, tws_common, 6);
    syscfg_write(CFG_TWS_CHANNEL, &tws_channel, 1);
    syscfg_write(CFG_TWS_PAIR_CODE_ID, (u8 *)&pair_code, 2);
    log_info("  CFG_BT_MAC_ADDR = 3C:00:0A:7E:1A:03");
    log_info("  CFG_TWS_PAIR_CODE_ID = 0x6699");
}
```

Then in `cfg_file_parse()`, add to the provisioning section:

```c
    // bt_provision_pair2_left_bud();   // Pair 2, Left bud (B03)
    // bt_provision_pair2_right_bud();  // Pair 2, Right bud (B04)
```

**Repeat this pattern for Pairs 3, 4, and 5** using the MAC addresses from the deployment table:

| Pair | Left MAC | Right MAC | Pair Code | Common ID |
|------|----------|-----------|-----------|-----------|
| P3 | `3C:00:0A:7E:1A:04` | `3C:00:0A:7E:1A:05` | `0x66AA` | `AA:BB:CC:00:03:FF` |
| P4 | `3C:00:0A:7E:1A:06` | `3C:00:0A:7E:1A:07` | `0x66BB` | `AA:BB:CC:00:04:FF` |
| P5 | `3C:00:0A:7E:1A:08` | `3C:00:0A:7E:1A:09` | `0x66CC` | `AA:BB:CC:00:05:FF` |

---

## Complete Provisioning Call Chain

```
Boot (Power On)
    ↓
app_main() → cfg_file_parse()
    ↓
TCFG_MANUAL_MAC_PROVISIONING_ENABLE check
    ↓
bt_provision_pair1_left_bud() [or appropriate pair function]
    ↓
All syscfg IDs written to persistent storage (BTIF/VM)
    ↓
Firmware continues with normal Bluetooth initialization
    ↓
Bud searches for sibling using CFG_TWS_REMOTE_ADDR
    ↓
TWS pairing completes (reciprocal sibling relationship verified)
```

---

## Important Notes

### 1. One Function Per Firmware Image
Only **ONE** provisioning function should be uncommented per firmware build. This ensures each bud gets its exact configuration.

### 2. Pair Code Must Match
Both buds in a pair must have the **same pair code** (e.g., both have `0x6688` for Pair 1). Different pairs must have **different pair codes** to prevent cross-pair interference.

### 3. Reciprocal Sibling Relationship
Always verify before building:
```
Left Bud's CFG_TWS_REMOTE_ADDR = Right Bud's CFG_TWS_LOCAL_ADDR ✓
Right Bud's CFG_TWS_REMOTE_ADDR = Left Bud's CFG_TWS_LOCAL_ADDR ✓
```

### 4. No Auto-Derivation
The provisioning functions use **explicit manual assignment**. No algorithmic MAC calculation occurs—each value is hardcoded in the function.

### 5. Persistence Across Power Cycles
Once provisioned via `syscfg_write()`, the MAC addresses persist in BTIF/VM storage. The bud will retain its identity even after power cycles.

### 6. Disabling Manual Provisioning
To revert to random MAC generation, set:
```c
#define TCFG_MANUAL_MAC_PROVISIONING_ENABLE  0
```

---

## Verification Checklist Before Factory Flash

- [ ] Uncommented EXACTLY ONE provisioning function
- [ ] Left & Right buds have same pair code (e.g., 0x6688)
- [ ] Left's TWS_REMOTE = Right's TWS_LOCAL
- [ ] Right's TWS_REMOTE = Left's TWS_LOCAL
- [ ] Common address is identical for both buds
- [ ] Channel ID: Left=0x00, Right=0x01
- [ ] Build succeeds (no compilation errors)
- [ ] Firmware binary created successfully

---

## Troubleshooting

| Symptom | Cause | Solution |
|---------|-------|----------|
| Buds don't pair | Mismatched CFG_TWS_REMOTE_ADDR | Verify reciprocal relationship in provisioning functions |
| Cross-pair interference | Same pair code on different pairs | Assign unique pair codes: 0x6688, 0x6699, 0x66AA, 0x66BB, 0x66CC |
| MAC addresses change on reboot | TCFG_MANUAL_MAC_PROVISIONING_ENABLE = 0 | Set to 1 and rebuild |
| Compilation error | Syntax error in provisioning function | Check function braces and semicolons |
| Both buds act as Left | Both have CFG_TWS_CHANNEL = 0x00 | Ensure Right bud has CFG_TWS_CHANNEL = 0x01 |

---

## Related Documentation

- [BT_CONFIG - Bluetooth Configuration Structure](../DOC%20LIBRARY/BT_CONFIG%20-%20Bluetooth%20Configuration%20Structure.md)
- [TWS Sibling Reciprocal Relationship - Configuration Guide](TWS%20SIBLING%20RECIPROCAL%20RELATIONSHIP%20-%20Configuration%20Guide.md)
- [MAC ADDRESS MASTER LIST - 10 Buds 5 Pairs](MAC%20ADDRESS%20MASTER%20LIST%20-%2010%20Buds%205%20Pairs.md)

