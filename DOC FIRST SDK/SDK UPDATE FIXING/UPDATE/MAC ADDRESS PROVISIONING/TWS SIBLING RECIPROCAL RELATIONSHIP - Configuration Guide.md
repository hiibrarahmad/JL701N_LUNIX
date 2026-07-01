# TWS Sibling Reciprocal Relationship - Configuration Guide

## Core Principle

Each earbud maintains a **reciprocal sibling relationship** through the `CFG_TWS_LOCAL_ADDR` and `CFG_TWS_REMOTE_ADDR` syscfg IDs:

- **Your own TWS identity** → `CFG_TWS_LOCAL_ADDR (95)`
- **Sibling's TWS identity** → `CFG_TWS_REMOTE_ADDR (96)`

**The Reciprocal Rule:**
```
Left Bud's CFG_TWS_REMOTE_ADDR = Right Bud's CFG_TWS_LOCAL_ADDR
Right Bud's CFG_TWS_REMOTE_ADDR = Left Bud's CFG_TWS_LOCAL_ADDR
```

This creates a bidirectional link so each bud knows exactly which device to search for during pairing and reconnection.

---

## Example: Single Pair (P1)

**Setup:**
- Left Earbud (B01): EDR MAC `3C:00:0A:7E:1A:00`
- Right Earbud (B02): EDR MAC `3C:00:0A:7E:1A:01`

### Left Bud (B01) Configuration

```c
CFG_BT_MAC_ADDR (102)       = 3C:00:0A:7E:1A:00     // Own EDR MAC
CFG_TWS_LOCAL_ADDR (95)     = 3C:00:0A:7E:1A:00     // Own TWS identity
CFG_TWS_REMOTE_ADDR (96)    = 3C:00:0A:7E:1A:01     // Sibling (Right) identity
CFG_TWS_COMMON_ADDR (97)    = AA:BB:CC:DD:EE:FF     // Shared pair identity
CFG_TWS_CHANNEL (98)        = 0x00                  // Left orientation
CFG_TWS_PAIR_CODE_ID (602)  = 0x6688                // Pair discovery code
```

### Right Bud (B02) Configuration

```c
CFG_BT_MAC_ADDR (102)       = 3C:00:0A:7E:1A:01     // Own EDR MAC
CFG_TWS_LOCAL_ADDR (95)     = 3C:00:0A:7E:1A:01     // Own TWS identity
CFG_TWS_REMOTE_ADDR (96)    = 3C:00:0A:7E:1A:00     // Sibling (Left) identity
CFG_TWS_COMMON_ADDR (97)    = AA:BB:CC:DD:EE:FF     // Shared pair identity
CFG_TWS_CHANNEL (98)        = 0x01                  // Right orientation
CFG_TWS_PAIR_CODE_ID (602)  = 0x6688                // Pair discovery code
```

### Verification

✅ **Left's `CFG_TWS_REMOTE_ADDR` (`3C:00:0A:7E:1A:01`) = Right's `CFG_TWS_LOCAL_ADDR` (`3C:00:0A:7E:1A:01`)**

✅ **Right's `CFG_TWS_REMOTE_ADDR` (`3C:00:0A:7E:1A:00`) = Left's `CFG_TWS_LOCAL_ADDR` (`3C:00:0A:7E:1A:00`)**

---

## Complete Multi-Pair Deployment Table

**For 5 Pairs × 2 Buds = 10 Total Units:**

| Pair | Bud | EDR MAC | TWS Local | TWS Remote | Pair Code | Channel | Common ID |
|------|-----|---------|-----------|------------|-----------|---------|-----------|
| **P1** | L (B01) | `3C:00:0A:7E:1A:00` | `3C:00:0A:7E:1A:00` | `3C:00:0A:7E:1A:01` | 0x6688 | 0x00 | `AA:BB:CC:00:01:FF` |
|  | R (B02) | `3C:00:0A:7E:1A:01` | `3C:00:0A:7E:1A:01` | `3C:00:0A:7E:1A:00` | 0x6688 | 0x01 | `AA:BB:CC:00:01:FF` |
| **P2** | L (B03) | `3C:00:0A:7E:1A:02` | `3C:00:0A:7E:1A:02` | `3C:00:0A:7E:1A:03` | 0x6699 | 0x00 | `AA:BB:CC:00:02:FF` |
|  | R (B04) | `3C:00:0A:7E:1A:03` | `3C:00:0A:7E:1A:03` | `3C:00:0A:7E:1A:02` | 0x6699 | 0x01 | `AA:BB:CC:00:02:FF` |
| **P3** | L (B05) | `3C:00:0A:7E:1A:04` | `3C:00:0A:7E:1A:04` | `3C:00:0A:7E:1A:05` | 0x66AA | 0x00 | `AA:BB:CC:00:03:FF` |
|  | R (B06) | `3C:00:0A:7E:1A:05` | `3C:00:0A:7E:1A:05` | `3C:00:0A:7E:1A:04` | 0x66AA | 0x01 | `AA:BB:CC:00:03:FF` |
| **P4** | L (B07) | `3C:00:0A:7E:1A:06` | `3C:00:0A:7E:1A:06` | `3C:00:0A:7E:1A:07` | 0x66BB | 0x00 | `AA:BB:CC:00:04:FF` |
|  | R (B08) | `3C:00:0A:7E:1A:07` | `3C:00:0A:7E:1A:07` | `3C:00:0A:7E:1A:06` | 0x66BB | 0x01 | `AA:BB:CC:00:04:FF` |
| **P5** | L (B09) | `3C:00:0A:7E:1A:08` | `3C:00:0A:7E:1A:08` | `3C:00:0A:7E:1A:09` | 0x66CC | 0x00 | `AA:BB:CC:00:05:FF` |
|  | R (B10) | `3C:00:0A:7E:1A:09` | `3C:00:0A:7E:1A:09` | `3C:00:0A:7E:1A:08` | 0x66CC | 0x01 | `AA:BB:CC:00:05:FF` |

---

## Key Observations

### 1. **EDR MAC = TWS Local Address (Simplified Approach)**
For simplicity, using the same value for both:
- `CFG_BT_MAC_ADDR` (what host sees in Bluetooth settings)
- `CFG_TWS_LOCAL_ADDR` (internal TWS identity)

This avoids maintaining two separate numbering schemes per bud.

### 2. **TWS Remote Always Points to Sibling**
The last byte increments by 1 for each bud pair:
```
Left:  3C:00:0A:7E:1A:00  →  Right: 3C:00:0A:7E:1A:01
Left:  3C:00:0A:7E:1A:02  →  Right: 3C:00:0A:7E:1A:03
Left:  3C:00:0A:7E:1A:04  →  Right: 3C:00:0A:7E:1A:05
...
```

### 3. **Pair Code Isolation**
Each pair gets a **unique pair code** to prevent cross-pair connections:
- Pair 1: `0x6688`
- Pair 2: `0x6699`
- Pair 3: `0x66AA`
- Pair 4: `0x66BB`
- Pair 5: `0x66CC`

### 4. **Common Address Shared**
Both buds in a pair share the same **Common Address** (`CFG_TWS_COMMON_ADDR`):
- Pair 1: `AA:BB:CC:00:01:FF` (both L & R)
- Pair 2: `AA:BB:CC:00:02:FF` (both L & R)
- etc.

This represents the pair as a single logical unit.

### 5. **Channel ID for Orientation**
```c
CFG_TWS_CHANNEL (98) = 0x00    // Left earbud
CFG_TWS_CHANNEL (98) = 0x01    // Right earbud
```

Firmware uses this to determine audio processing direction (which ear gets which channel mix).

---

## Verification Checklist

For each pair, verify before flashing:

### Pair P1 (Left B01, Right B02):

```
✅ B01 TWS_LOCAL   = 3C:00:0A:7E:1A:00
✅ B01 TWS_REMOTE  = 3C:00:0A:7E:1A:01  (matches B02 TWS_LOCAL)
✅ B02 TWS_LOCAL   = 3C:00:0A:7E:1A:01
✅ B02 TWS_REMOTE  = 3C:00:0A:7E:1A:00  (matches B01 TWS_LOCAL)
✅ B01 PAIR_CODE   = 0x6688
✅ B02 PAIR_CODE   = 0x6688  (same)
✅ B01 COMMON_ADDR = AA:BB:CC:00:01:FF
✅ B02 COMMON_ADDR = AA:BB:CC:00:01:FF  (same)
```

### Repeat for Pairs P2-P5

---

## Factory Flash Workflow

### Step 1: Build 10 Firmware Images
```bash
# For Left Buds (even MACs)
build_firmware.sh P1_LEFT   3C:00:0A:7E:1A:00  B01
build_firmware.sh P2_LEFT   3C:00:0A:7E:1A:02  B03
build_firmware.sh P3_LEFT   3C:00:0A:7E:1A:04  B05
build_firmware.sh P4_LEFT   3C:00:0A:7E:1A:06  B07
build_firmware.sh P5_LEFT   3C:00:0A:7E:1A:08  B09

# For Right Buds (odd MACs)
build_firmware.sh P1_RIGHT  3C:00:0A:7E:1A:01  B02
build_firmware.sh P2_RIGHT  3C:00:0A:7E:1A:03  B04
build_firmware.sh P3_RIGHT  3C:00:0A:7E:1A:05  B06
build_firmware.sh P4_RIGHT  3C:00:0A:7E:1A:07  B08
build_firmware.sh P5_RIGHT  3C:00:0A:7E:1A:09  B10
```

### Step 2: Flash Each Bud
```bash
# Pair 1
jlink_flash P1_LEFT.bin  B01_UNIT_ID
jlink_flash P1_RIGHT.bin B02_UNIT_ID

# Pair 2
jlink_flash P2_LEFT.bin  B03_UNIT_ID
jlink_flash P2_RIGHT.bin B04_UNIT_ID

# ... repeat for P3-P5
```

### Step 3: Verification Test
```bash
# Power on both buds of Pair 1
# Expected: TWS pairing within 5-10 seconds
# Verify: No cross-pair interference
# Repeat for Pairs 2-5
```

---

## Code Integration Points

### In user_cfg.c (cfg_file_parse function):

```c
// Manual provisioning example (no auto-derivation)
syscfg_read(CFG_BT_MAC_ADDR, mac_buf, 6);           // Load own EDR MAC
syscfg_read(CFG_TWS_LOCAL_ADDR, tws_local, 6);      // Load own TWS identity
syscfg_read(CFG_TWS_REMOTE_ADDR, tws_remote, 6);    // Load sibling identity
syscfg_read(CFG_TWS_COMMON_ADDR, common_addr, 6);   // Load pair identity
syscfg_read(CFG_TWS_CHANNEL, &channel, 1);          // Load orientation (L=0, R=1)
syscfg_read(CFG_TWS_PAIR_CODE_ID, &pair_code, 2);  // Load pair discovery code

memcpy(bt_cfg.mac_addr, mac_buf, 6);
memcpy(bt_cfg.tws_local_addr, tws_local, 6);
```

### In bt_tws.c (sibling discovery):

```c
// Search for sibling using TWS_REMOTE_ADDR
extern int tws_get_sibling_addr(u8 *addr, int *result);

u8 sibling_addr[6];
int pairing_result = 0;
syscfg_read(CFG_TWS_REMOTE_ADDR, sibling_addr, 6);  // Read target sibling MAC
tws_get_sibling_addr(sibling_addr, &pairing_result); // Search & connect
```

---

## Common Pitfalls & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Buds don't pair | Mismatched TWS_REMOTE addresses | Verify reciprocal relationship: Left's REMOTE = Right's LOCAL |
| Cross-pair interference | Same pair code for different pairs | Assign unique pair codes (0x6688, 0x6699, 0x66AA, etc.) |
| One bud always master | Channel ID incorrect | Set CFG_TWS_CHANNEL: 0x00=Left, 0x01=Right |
| Random MAC on each boot | All 0xFF in syscfg | Pre-flash MAC values to BTIF region (CFG_BT_MAC_ADDR) |
| Sibling not found | Common pair code mismatch | Ensure both L & R have identical CFG_TWS_PAIR_CODE_ID |

---

## Summary

The **reciprocal sibling relationship** is the foundation of TWS pairing on JL7016G:

1. **Each bud stores its own identity** in `CFG_TWS_LOCAL_ADDR`
2. **Each bud stores sibling's identity** in `CFG_TWS_REMOTE_ADDR`
3. **The addresses must be reciprocal** (each bud's LOCAL = other's REMOTE)
4. **Unique pair codes** prevent cross-pair interference
5. **No automatic derivation** — all values manually assigned per firmware image

This ensures deterministic, explicit control over pair membership with zero latency overhead or auto-derivation calculations.

