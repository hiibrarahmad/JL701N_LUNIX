---
tags: [mac, provisioning, multi-pair, bud-identity, tws, centralized, how-to]
date: 2026-06-09
board: JL7016G Hybrid
chip: AC701N (BR28)
status: Reference guide — example for Pairs 2, 3, 4
effort: Low
---

# 🔧 MULTI-PAIR EXPANSION GUIDE — Adding Pairs 2, 3, 4 to the Centralized System

> **Read [BUD IDENTITY — Centralized Config System](BUD%20IDENTITY%20%E2%80%94%20Centralized%20MAC%20and%20Pair%20Configuration%20System.md) first.**  
> That doc explains the single-source system already in place for Pair 1.  
> This doc shows exactly how to add Pairs 2, 3, and 4 following the same pattern.

---

## Quick Reference — All 8 Buds (Pairs 1–4)

| Pair | Unit | Role  | Local EDR MAC       | Sibling MAC         | Common MAC          | Pair Code | Channel |
| ---- | ---- | ----- | ------------------- | ------------------- | ------------------- | --------- | ------- |
| P01  | B01  | Left  | `3C:00:0A:7E:1A:00` | `3C:00:0A:7E:1A:01` | `AA:BB:CC:00:01:FF` | 0x6688    | 0x00    |
| P01  | B02  | Right | `3C:00:0A:7E:1A:01` | `3C:00:0A:7E:1A:00` | `AA:BB:CC:00:01:FF` | 0x6688    | 0x01    |
| P02  | B03  | Left  | `3C:00:0A:7E:1A:02` | `3C:00:0A:7E:1A:03` | `AA:BB:CC:00:02:FF` | 0x6688    | 0x00    |
| P02  | B04  | Right | `3C:00:0A:7E:1A:03` | `3C:00:0A:7E:1A:02` | `AA:BB:CC:00:02:FF` | 0x6688    | 0x01    |
| P03  | B05  | Left  | `3C:00:0A:7E:1A:04` | `3C:00:0A:7E:1A:05` | `AA:BB:CC:00:03:FF` | 0x6688    | 0x00    |
| P03  | B06  | Right | `3C:00:0A:7E:1A:05` | `3C:00:0A:7E:1A:04` | `AA:BB:CC:00:03:FF` | 0x6688    | 0x01    |
| P04  | B07  | Left  | `3C:00:0A:7E:1A:06` | `3C:00:0A:7E:1A:07` | `AA:BB:CC:00:04:FF` | 0x6688    | 0x00    |
| P04  | B08  | Right | `3C:00:0A:7E:1A:07` | `3C:00:0A:7E:1A:06` | `AA:BB:CC:00:04:FF` | 0x6688    | 0x01    |

> **Sibling rule:** Local MAC is always written to itself. Sibling MAC is always the other bud in the same pair.  
> **Common MAC:** Unique per pair — this is what makes two buds find each other during TWS discovery.

---

## MAC Naming Convention

```
3C:00:0A:7E:1A:XX
                ^^— last byte increments by +1 per bud, in flash order
                    B01=00, B02=01, B03=02, B04=03, B05=04 ...

AA:BB:CC:00:0Y:FF
              ^— Y = pair number (P01=01, P02=02, P03=03, P04=04)
```

Pair code `0x6688` is the same for all pairs. Pairs are distinguished by their unique common MAC, not the code.

---

## Two Files to Edit

All changes live in exactly two files:

| File | What to add |
|------|------------|
| `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h` | P2_*, P3_*, P4_* MAC defines + THIS_PAIR selector |
| `apps/earphone/user_cfg.c` | Forward declarations + provisioning functions + updated auto-select block |

---

## STEP 1 — board_jl7016g_hybrid_cfg.h

### Where to find it

Open `board_jl7016g_hybrid_cfg.h`. Find the BUD IDENTITY block near the top (~line 26). It currently ends after the P1_* defines and the `THIS_BUD` line.

### Current state (already in file)

```c
#define BUD_LEFT    0
#define BUD_RIGHT   1

#define P1_LEFT_MAC      {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x00}
#define P1_RIGHT_MAC     {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x01}
#define P1_COMMON_MAC    {0xAA, 0xBB, 0xCC, 0x00, 0x01, 0xFF}
#define P1_PAIR_CODE     0x6688

//  ▼▼▼  CHANGE ONLY THIS LINE PER FIRMWARE IMAGE  ▼▼▼
#define THIS_BUD         BUD_RIGHT

#define TCFG_RIGHT_BUD   THIS_BUD
```

### What to add — paste after the P1_* block, before THIS_BUD

```c
// Pair 2 — B03 (Left) + B04 (Right)
#define P2_LEFT_MAC      {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x02}
#define P2_RIGHT_MAC     {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x03}
#define P2_COMMON_MAC    {0xAA, 0xBB, 0xCC, 0x00, 0x02, 0xFF}
#define P2_PAIR_CODE     0x6688

// Pair 3 — B05 (Left) + B06 (Right)
#define P3_LEFT_MAC      {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x04}
#define P3_RIGHT_MAC     {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x05}
#define P3_COMMON_MAC    {0xAA, 0xBB, 0xCC, 0x00, 0x03, 0xFF}
#define P3_PAIR_CODE     0x6688

// Pair 4 — B07 (Left) + B08 (Right)
#define P4_LEFT_MAC      {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x06}
#define P4_RIGHT_MAC     {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x07}
#define P4_COMMON_MAC    {0xAA, 0xBB, 0xCC, 0x00, 0x04, 0xFF}
#define P4_PAIR_CODE     0x6688
```

### What to change — the two selector lines

Replace the current selector block:

```c
// BEFORE (Pair 1 only)
#define THIS_BUD         BUD_RIGHT
#define TCFG_RIGHT_BUD   THIS_BUD
```

With the two-selector version:

```c
//  ▼▼▼  CHANGE THESE TWO LINES PER FIRMWARE IMAGE  ▼▼▼
#define THIS_PAIR        1          // 1=P01, 2=P02, 3=P03, 4=P04
#define THIS_BUD         BUD_RIGHT  // BUD_RIGHT or BUD_LEFT

// Derived — do not edit below this line
#define TCFG_RIGHT_BUD   THIS_BUD
```

### Full BUD IDENTITY block after edits

```c
//*******************************************************************************//
//              BUD IDENTITY — SINGLE POINT OF CHANGE PER FIRMWARE BUILD          //
//                                                                                 //
//  Set THIS_PAIR and THIS_BUD. All downstream config follows.                    //
//  THIS_PAIR: 1=P01(B01/B02)  2=P02(B03/B04)  3=P03(B05/B06)  4=P04(B07/B08)  //
//  THIS_BUD:  BUD_RIGHT → Hold=VolUp / DoubleTap=Next                            //
//             BUD_LEFT  → Hold=VolDown/ DoubleTap=Prev                           //
//*******************************************************************************//
#define BUD_LEFT    0
#define BUD_RIGHT   1

// Pair 1 — B01 (Left) + B02 (Right)
#define P1_LEFT_MAC      {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x00}
#define P1_RIGHT_MAC     {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x01}
#define P1_COMMON_MAC    {0xAA, 0xBB, 0xCC, 0x00, 0x01, 0xFF}
#define P1_PAIR_CODE     0x6688

// Pair 2 — B03 (Left) + B04 (Right)
#define P2_LEFT_MAC      {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x02}
#define P2_RIGHT_MAC     {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x03}
#define P2_COMMON_MAC    {0xAA, 0xBB, 0xCC, 0x00, 0x02, 0xFF}
#define P2_PAIR_CODE     0x6688

// Pair 3 — B05 (Left) + B06 (Right)
#define P3_LEFT_MAC      {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x04}
#define P3_RIGHT_MAC     {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x05}
#define P3_COMMON_MAC    {0xAA, 0xBB, 0xCC, 0x00, 0x03, 0xFF}
#define P3_PAIR_CODE     0x6688

// Pair 4 — B07 (Left) + B08 (Right)
#define P4_LEFT_MAC      {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x06}
#define P4_RIGHT_MAC     {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x07}
#define P4_COMMON_MAC    {0xAA, 0xBB, 0xCC, 0x00, 0x04, 0xFF}
#define P4_PAIR_CODE     0x6688

//  ▼▼▼  CHANGE THESE TWO LINES PER FIRMWARE IMAGE  ▼▼▼
#define THIS_PAIR        1          // 1=P01, 2=P02, 3=P03, 4=P04
#define THIS_BUD         BUD_RIGHT  // BUD_RIGHT or BUD_LEFT

// Derived — do not edit below this line
#define TCFG_RIGHT_BUD   THIS_BUD
```

---

## STEP 2 — user_cfg.c, Forward Declarations

### Where to find it

Open `user_cfg.c`. Find the forward declaration block near the top (~line 31):

```c
#if TCFG_MANUAL_MAC_PROVISIONING_ENABLE
void bt_provision_pair1_left_bud(void);
void bt_provision_pair1_right_bud(void);
#endif
```

### What to add — paste after the existing two declarations

```c
void bt_provision_pair2_left_bud(void);
void bt_provision_pair2_right_bud(void);
void bt_provision_pair3_left_bud(void);
void bt_provision_pair3_right_bud(void);
void bt_provision_pair4_left_bud(void);
void bt_provision_pair4_right_bud(void);
```

---

## STEP 3 — user_cfg.c, Auto-Select Block

### Where to find it

Find the provisioning call block (~line 543):

```c
// Current state — Pair 1 only
#if TCFG_MANUAL_MAC_PROVISIONING_ENABLE
    // Automatic — driven by THIS_BUD in board_jl7016g_hybrid_cfg.h
#if TCFG_RIGHT_BUD
    bt_provision_pair1_right_bud();
#else
    bt_provision_pair1_left_bud();
#endif
#endif
```

### Replace the entire block with this

```c
#if TCFG_MANUAL_MAC_PROVISIONING_ENABLE
    // Pair and bud selected by THIS_PAIR and THIS_BUD in board_jl7016g_hybrid_cfg.h
#if THIS_PAIR == 1
  #if TCFG_RIGHT_BUD
    bt_provision_pair1_right_bud();
  #else
    bt_provision_pair1_left_bud();
  #endif
#elif THIS_PAIR == 2
  #if TCFG_RIGHT_BUD
    bt_provision_pair2_right_bud();
  #else
    bt_provision_pair2_left_bud();
  #endif
#elif THIS_PAIR == 3
  #if TCFG_RIGHT_BUD
    bt_provision_pair3_right_bud();
  #else
    bt_provision_pair3_left_bud();
  #endif
#elif THIS_PAIR == 4
  #if TCFG_RIGHT_BUD
    bt_provision_pair4_right_bud();
  #else
    bt_provision_pair4_left_bud();
  #endif
#endif
#endif
```

---

## STEP 4 — user_cfg.c, New Provisioning Functions

### Where to add

Paste these functions at the end of `user_cfg.c`, after `bt_provision_pair1_right_bud()`.

### Pair 2 — Left Bud (B03)

```c
void bt_provision_pair2_left_bud(void)
{
    u8 edr_mac[6]    = P2_LEFT_MAC;
    u8 tws_local[6]  = P2_LEFT_MAC;
    u8 tws_remote[6] = P2_RIGHT_MAC;
    u8 tws_common[6] = P2_COMMON_MAC;
    u8 tws_channel   = BUD_LEFT;
    u16 pair_code    = P2_PAIR_CODE;

    log_info("Provisioning Pair 2 - LEFT BUD (B03)");
    syscfg_write(CFG_BT_MAC_ADDR,      edr_mac,              6);
    syscfg_write(CFG_TWS_LOCAL_ADDR,   tws_local,            6);
    syscfg_write(CFG_TWS_REMOTE_ADDR,  tws_remote,           6);
    syscfg_write(CFG_TWS_COMMON_ADDR,  tws_common,           6);
    syscfg_write(CFG_TWS_CHANNEL,      &tws_channel,         1);
    syscfg_write(CFG_TWS_PAIR_CODE_ID, (u8 *)&pair_code,     2);

    memcpy(manual_cfg_mac_override, edr_mac, 6);
    manual_cfg_mac_override_valid = 1;
}
```

### Pair 2 — Right Bud (B04)

```c
void bt_provision_pair2_right_bud(void)
{
    u8 edr_mac[6]    = P2_RIGHT_MAC;
    u8 tws_local[6]  = P2_RIGHT_MAC;
    u8 tws_remote[6] = P2_LEFT_MAC;
    u8 tws_common[6] = P2_COMMON_MAC;
    u8 tws_channel   = BUD_RIGHT;
    u16 pair_code    = P2_PAIR_CODE;

    log_info("Provisioning Pair 2 - RIGHT BUD (B04)");
    syscfg_write(CFG_BT_MAC_ADDR,      edr_mac,              6);
    syscfg_write(CFG_TWS_LOCAL_ADDR,   tws_local,            6);
    syscfg_write(CFG_TWS_REMOTE_ADDR,  tws_remote,           6);
    syscfg_write(CFG_TWS_COMMON_ADDR,  tws_common,           6);
    syscfg_write(CFG_TWS_CHANNEL,      &tws_channel,         1);
    syscfg_write(CFG_TWS_PAIR_CODE_ID, (u8 *)&pair_code,     2);

    memcpy(manual_cfg_mac_override, edr_mac, 6);
    manual_cfg_mac_override_valid = 1;
}
```

### Pair 3 — Left Bud (B05)

```c
void bt_provision_pair3_left_bud(void)
{
    u8 edr_mac[6]    = P3_LEFT_MAC;
    u8 tws_local[6]  = P3_LEFT_MAC;
    u8 tws_remote[6] = P3_RIGHT_MAC;
    u8 tws_common[6] = P3_COMMON_MAC;
    u8 tws_channel   = BUD_LEFT;
    u16 pair_code    = P3_PAIR_CODE;

    log_info("Provisioning Pair 3 - LEFT BUD (B05)");
    syscfg_write(CFG_BT_MAC_ADDR,      edr_mac,              6);
    syscfg_write(CFG_TWS_LOCAL_ADDR,   tws_local,            6);
    syscfg_write(CFG_TWS_REMOTE_ADDR,  tws_remote,           6);
    syscfg_write(CFG_TWS_COMMON_ADDR,  tws_common,           6);
    syscfg_write(CFG_TWS_CHANNEL,      &tws_channel,         1);
    syscfg_write(CFG_TWS_PAIR_CODE_ID, (u8 *)&pair_code,     2);

    memcpy(manual_cfg_mac_override, edr_mac, 6);
    manual_cfg_mac_override_valid = 1;
}
```

### Pair 3 — Right Bud (B06)

```c
void bt_provision_pair3_right_bud(void)
{
    u8 edr_mac[6]    = P3_RIGHT_MAC;
    u8 tws_local[6]  = P3_RIGHT_MAC;
    u8 tws_remote[6] = P3_LEFT_MAC;
    u8 tws_common[6] = P3_COMMON_MAC;
    u8 tws_channel   = BUD_RIGHT;
    u16 pair_code    = P3_PAIR_CODE;

    log_info("Provisioning Pair 3 - RIGHT BUD (B06)");
    syscfg_write(CFG_BT_MAC_ADDR,      edr_mac,              6);
    syscfg_write(CFG_TWS_LOCAL_ADDR,   tws_local,            6);
    syscfg_write(CFG_TWS_REMOTE_ADDR,  tws_remote,           6);
    syscfg_write(CFG_TWS_COMMON_ADDR,  tws_common,           6);
    syscfg_write(CFG_TWS_CHANNEL,      &tws_channel,         1);
    syscfg_write(CFG_TWS_PAIR_CODE_ID, (u8 *)&pair_code,     2);

    memcpy(manual_cfg_mac_override, edr_mac, 6);
    manual_cfg_mac_override_valid = 1;
}
```

### Pair 4 — Left Bud (B07)

```c
void bt_provision_pair4_left_bud(void)
{
    u8 edr_mac[6]    = P4_LEFT_MAC;
    u8 tws_local[6]  = P4_LEFT_MAC;
    u8 tws_remote[6] = P4_RIGHT_MAC;
    u8 tws_common[6] = P4_COMMON_MAC;
    u8 tws_channel   = BUD_LEFT;
    u16 pair_code    = P4_PAIR_CODE;

    log_info("Provisioning Pair 4 - LEFT BUD (B07)");
    syscfg_write(CFG_BT_MAC_ADDR,      edr_mac,              6);
    syscfg_write(CFG_TWS_LOCAL_ADDR,   tws_local,            6);
    syscfg_write(CFG_TWS_REMOTE_ADDR,  tws_remote,           6);
    syscfg_write(CFG_TWS_COMMON_ADDR,  tws_common,           6);
    syscfg_write(CFG_TWS_CHANNEL,      &tws_channel,         1);
    syscfg_write(CFG_TWS_PAIR_CODE_ID, (u8 *)&pair_code,     2);

    memcpy(manual_cfg_mac_override, edr_mac, 6);
    manual_cfg_mac_override_valid = 1;
}
```

### Pair 4 — Right Bud (B08)

```c
void bt_provision_pair4_right_bud(void)
{
    u8 edr_mac[6]    = P4_RIGHT_MAC;
    u8 tws_local[6]  = P4_RIGHT_MAC;
    u8 tws_remote[6] = P4_LEFT_MAC;
    u8 tws_common[6] = P4_COMMON_MAC;
    u8 tws_channel   = BUD_RIGHT;
    u16 pair_code    = P4_PAIR_CODE;

    log_info("Provisioning Pair 4 - RIGHT BUD (B08)");
    syscfg_write(CFG_BT_MAC_ADDR,      edr_mac,              6);
    syscfg_write(CFG_TWS_LOCAL_ADDR,   tws_local,            6);
    syscfg_write(CFG_TWS_REMOTE_ADDR,  tws_remote,           6);
    syscfg_write(CFG_TWS_COMMON_ADDR,  tws_common,           6);
    syscfg_write(CFG_TWS_CHANNEL,      &tws_channel,         1);
    syscfg_write(CFG_TWS_PAIR_CODE_ID, (u8 *)&pair_code,     2);

    memcpy(manual_cfg_mac_override, edr_mac, 6);
    manual_cfg_mac_override_valid = 1;
}
```

---

## Build Matrix — 8 Firmware Images

To produce all 8 images, change only `THIS_PAIR` and `THIS_BUD` in `board_jl7016g_hybrid_cfg.h`:

| Image | THIS_PAIR | THIS_BUD | Output firmware | Flashes to |
|-------|-----------|----------|-----------------|------------|
| P01-L | `1` | `BUD_LEFT` | pair1_left.bin | B01 |
| P01-R | `1` | `BUD_RIGHT` | pair1_right.bin | B02 |
| P02-L | `2` | `BUD_LEFT` | pair2_left.bin | B03 |
| P02-R | `2` | `BUD_RIGHT` | pair2_right.bin | B04 |
| P03-L | `3` | `BUD_LEFT` | pair3_left.bin | B05 |
| P03-R | `3` | `BUD_RIGHT` | pair3_right.bin | B06 |
| P04-L | `4` | `BUD_LEFT` | pair4_left.bin | B07 |
| P04-R | `4` | `BUD_RIGHT` | pair4_right.bin | B08 |

---

## Checklist Before Flashing Each Image

- [ ] `THIS_PAIR` set to correct pair number
- [ ] `THIS_BUD` set to `BUD_LEFT` or `BUD_RIGHT`
- [ ] Build completed without errors
- [ ] Flash to the correct physical unit (match Unit ID label on bud)
- [ ] After first boot, verify boot log shows `Provisioning Pair X - LEFT/RIGHT BUD (BXX)`
- [ ] Pair both buds from the same pair together — they must find each other via common MAC

---

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Flashed P01-R firmware to left physical bud | Vol Up/Down inverted; TWS won't pair | Re-flash with correct left image |
| Both buds flashed with same role (both right) | TWS discovery fails — both are looking for the other as remote | One must be re-flashed as left |
| THIS_PAIR wrong (e.g., 1 instead of 2) | Bud broadcasts Pair 1 MAC, won't pair with Pair 2 sibling | Re-flash with correct pair number |
| Common MAC differs between siblings | TWS page scan never succeeds | Both siblings must use same `PX_COMMON_MAC` |

---

## Related Documents

- [→ BUD IDENTITY — Centralized Config System](BUD%20IDENTITY%20%E2%80%94%20Centralized%20MAC%20and%20Pair%20Configuration%20System.md)
- [→ MAC ADDRESS MASTER LIST — 10 Buds 5 Pairs](MAC%20ADDRESS%20MASTER%20LIST%20-%2010%20Buds%205%20Pairs.md)
- [→ TWS SIBLING RECIPROCAL RELATIONSHIP](TWS%20SIBLING%20RECIPROCAL%20RELATIONSHIP%20-%20Configuration%20Guide.md)
- [→ FACTORY FLASH WORKFLOW](FACTORY%20FLASH%20WORKFLOW%20-%20Manual%20Pair%20Mapping.md)
- [→ SDK IMPLEMENTATION — Manual MAC Provisioning Functions](SDK%20IMPLEMENTATION%20-%20Manual%20MAC%20Provisioning%20Functions.md)
