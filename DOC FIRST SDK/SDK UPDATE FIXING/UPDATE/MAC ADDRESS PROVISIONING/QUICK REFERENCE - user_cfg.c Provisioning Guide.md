# Quick Reference - MAC Provisioning in user_cfg.c

## Where the Code Is Located

**File:** `apps/earphone/user_cfg.c`

### Two Locations:

#### 1. Provisioning Entry Point (Line ~540)
```c
cfg_file_parse() {
    ...
    /*** MANUAL MAC PROVISIONING ENTRY POINT ***/
    #if TCFG_MANUAL_MAC_PROVISIONING_ENABLE
        // bt_provision_pair1_left_bud();   // UNCOMMENT for B01
        // bt_provision_pair1_right_bud();  // UNCOMMENT for B02
    #endif
    /*** END MANUAL MAC PROVISIONING ***/
    ...
}
```

#### 2. Provisioning Functions (End of file, before `bt_modify_name()`)
```c
//======================================================================================//
//              MAC ADDRESS PROVISIONING - Manual Per-Pair Configuration              //
//======================================================================================//

void bt_provision_pair1_left_bud(void)  {
    // Pair 1, Left Bud (B01)
    // EDR MAC: 3C:00:0A:7E:1A:00
    // TWS Local: 3C:00:0A:7E:1A:00
    // TWS Remote: 3C:00:0A:7E:1A:01 (sibling)
    // Pair Code: 0x6688
    // Channel: 0x00 (LEFT)
}

void bt_provision_pair1_right_bud(void) {
    // Pair 1, Right Bud (B02)
    // EDR MAC: 3C:00:0A:7E:1A:01
    // TWS Local: 3C:00:0A:7E:1A:01
    // TWS Remote: 3C:00:0A:7E:1A:00 (sibling)
    // Pair Code: 0x6688
    // Channel: 0x01 (RIGHT)
}
```

---

## How to Use

### Building Pair 1 - Left Bud (B01)

```c
// In cfg_file_parse(), line ~545:

#if TCFG_MANUAL_MAC_PROVISIONING_ENABLE
    bt_provision_pair1_left_bud();   // ← UNCOMMENT THIS
    // bt_provision_pair1_right_bud();
#endif
```

Then build:
```bash
.vscode/winmk.bat all
→ firmware_P1_LEFT.bin
```

### Building Pair 1 - Right Bud (B02)

```c
// In cfg_file_parse(), line ~545:

#if TCFG_MANUAL_MAC_PROVISIONING_ENABLE
    // bt_provision_pair1_left_bud();
    bt_provision_pair1_right_bud();  // ← UNCOMMENT THIS
#endif
```

Then build:
```bash
.vscode/winmk.bat all
→ firmware_P1_RIGHT.bin
```

### Flash Both Buds

```bash
# Flash Left (B01)
jlink_flash firmware_P1_LEFT.bin

# Flash Right (B02)
jlink_flash firmware_P1_RIGHT.bin

# Power on both buds → TWS pairing within 5-10 seconds
```

---

## What Gets Provisioned to Each Bud

### Left Bud (B01) Syscfg Storage:

| ID | Name | Value | Purpose |
|----|------|-------|---------|
| 102 | CFG_BT_MAC_ADDR | `3C:00:0A:7E:1A:00` | Own EDR MAC (what phone sees) |
| 95 | CFG_TWS_LOCAL_ADDR | `3C:00:0A:7E:1A:00` | Own TWS identity |
| 96 | CFG_TWS_REMOTE_ADDR | `3C:00:0A:7E:1A:01` | Sibling (Right) identity |
| 97 | CFG_TWS_COMMON_ADDR | `AA:BB:CC:00:01:FF` | Pair shared identity |
| 98 | CFG_TWS_CHANNEL | `0x00` | Left orientation |
| 602 | CFG_TWS_PAIR_CODE_ID | `0x6688` | Pair discovery code |

### Right Bud (B02) Syscfg Storage:

| ID | Name | Value | Purpose |
|----|------|-------|---------|
| 102 | CFG_BT_MAC_ADDR | `3C:00:0A:7E:1A:01` | Own EDR MAC |
| 95 | CFG_TWS_LOCAL_ADDR | `3C:00:0A:7E:1A:01` | Own TWS identity |
| 96 | CFG_TWS_REMOTE_ADDR | `3C:00:0A:7E:1A:00` | Sibling (Left) identity |
| 97 | CFG_TWS_COMMON_ADDR | `AA:BB:CC:00:01:FF` | Pair shared identity |
| 98 | CFG_TWS_CHANNEL | `0x01` | Right orientation |
| 602 | CFG_TWS_PAIR_CODE_ID | `0x6688` | Pair discovery code |

---

## Reciprocal Verification

Before flashing, verify:

✅ **Left's TWS_REMOTE (`3C:00:0A:7E:1A:01`) = Right's TWS_LOCAL (`3C:00:0A:7E:1A:01`)**

✅ **Right's TWS_REMOTE (`3C:00:0A:7E:1A:00`) = Left's TWS_LOCAL (`3C:00:0A:7E:1A:00`)**

✅ **Both have same pair code: `0x6688`**

✅ **Left channel: `0x00`, Right channel: `0x01`**

---

## Adding More Pairs (P2-P5)

### Pattern for Pair 2 (P2):

Add this template and fill in the values:

```c
void bt_provision_pair2_left_bud(void)
{
    u8 edr_mac[6]        = {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x02};  // ← Left MAC
    u8 tws_local[6]      = {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x02};  // ← Same as above
    u8 tws_remote[6]     = {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x03};  // ← Right MAC
    u8 tws_common[6]     = {0xAA, 0xBB, 0xCC, 0x00, 0x02, 0xFF};  // ← Change 02
    u8 tws_channel       = 0x00;                                   // ← 0x00 for Left
    u16 pair_code        = 0x6699;                                 // ← Unique code

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
    u8 edr_mac[6]        = {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x03};  // ← Right MAC
    u8 tws_local[6]      = {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x03};  // ← Same as above
    u8 tws_remote[6]     = {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x02};  // ← Left MAC
    u8 tws_common[6]     = {0xAA, 0xBB, 0xCC, 0x00, 0x02, 0xFF};  // ← Change 02
    u8 tws_channel       = 0x01;                                   // ← 0x01 for Right
    u16 pair_code        = 0x6699;                                 // ← Same as Left

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

Then in `cfg_file_parse()`:

```c
#if TCFG_MANUAL_MAC_PROVISIONING_ENABLE
    // bt_provision_pair1_left_bud();
    // bt_provision_pair1_right_bud();
    // bt_provision_pair2_left_bud();   // ← UNCOMMENT for B03
    // bt_provision_pair2_right_bud();  // ← UNCOMMENT for B04
#endif
```

### MAC Values Reference Table for P3-P5:

| Pair | Left MAC | Right MAC | Pair Code | Common ID Suffix |
|------|----------|-----------|-----------|------------------|
| P1 | `3C:00:0A:7E:1A:00` | `3C:00:0A:7E:1A:01` | `0x6688` | `00:01:FF` |
| P2 | `3C:00:0A:7E:1A:02` | `3C:00:0A:7E:1A:03` | `0x6699` | `00:02:FF` |
| P3 | `3C:00:0A:7E:1A:04` | `3C:00:0A:7E:1A:05` | `0x66AA` | `00:03:FF` |
| P4 | `3C:00:0A:7E:1A:06` | `3C:00:0A:7E:1A:07` | `0x66BB` | `00:04:FF` |
| P5 | `3C:00:0A:7E:1A:08` | `3C:00:0A:7E:1A:09` | `0x66CC` | `00:05:FF` |

---

## Boot Log Verification

### When Left Bud (B01) boots:

```
[USER_CFG] Provisioning Pair 1 - LEFT BUD (B01)
[USER_CFG]   CFG_BT_MAC_ADDR (102) = 3C:00:0A:7E:1A:00
[USER_CFG]   CFG_TWS_LOCAL_ADDR (95) = 3C:00:0A:7E:1A:00
[USER_CFG]   CFG_TWS_REMOTE_ADDR (96) = 3C:00:0A:7E:1A:01 [sibling]
[USER_CFG]   CFG_TWS_COMMON_ADDR (97) = AA:BB:CC:00:01:FF [pair]
[USER_CFG]   CFG_TWS_CHANNEL (98) = 0x00 [LEFT]
[USER_CFG]   CFG_TWS_PAIR_CODE_ID (602) = 0x6688
```

### When Right Bud (B02) boots:

```
[USER_CFG] Provisioning Pair 1 - RIGHT BUD (B02)
[USER_CFG]   CFG_BT_MAC_ADDR (102) = 3C:00:0A:7E:1A:01
[USER_CFG]   CFG_TWS_LOCAL_ADDR (95) = 3C:00:0A:7E:1A:01
[USER_CFG]   CFG_TWS_REMOTE_ADDR (96) = 3C:00:0A:7E:1A:00 [sibling]
[USER_CFG]   CFG_TWS_COMMON_ADDR (97) = AA:BB:CC:00:01:FF [pair]
[USER_CFG]   CFG_TWS_CHANNEL (98) = 0x01 [RIGHT]
[USER_CFG]   CFG_TWS_PAIR_CODE_ID (602) = 0x6688
```

✅ If you see this in the logs, provisioning succeeded!

---

## Disable Manual Provisioning

To revert to random MAC generation:

```c
#define TCFG_MANUAL_MAC_PROVISIONING_ENABLE  0  // ← Change to 0
```

Then rebuild. The firmware will fall back to generating random MAC addresses on each boot.

