---
tags: [bud-identity, mac, provisioning, configuration, left-right, tws, centralized]
date: 2026-06-09
board: JL7016G Hybrid
chip: AC701N (BR28)
status: Implemented
files_modified:
  - apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h
  - apps/earphone/user_cfg.c
---

# 🎧 BUD IDENTITY — Centralized MAC and Pair Configuration System

## Problem This Solved

Before this change, building a left vs right bud firmware image required editing **two separate files** and keeping them in sync manually:

1. `board_jl7016g_hybrid_cfg.h` — change `TCFG_RIGHT_BUD` (0 or 1) to select key table
2. `user_cfg.c` — manually comment/uncomment the correct provisioning call

If only one was changed, the firmware would ship with mismatched key behavior and MAC addresses — a silent bug that would cause wrong volume direction and failed TWS pairing.

Additionally, the MAC addresses and pair code were duplicated as raw byte arrays inside two separate functions, so changing a MAC required editing four separate places (two functions × two bytes-arrays each).

---

## The New System — Single Point of Change

Everything is now driven from **one line** in the board config header:

```c
// apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h

//  ▼▼▼  CHANGE ONLY THIS LINE PER FIRMWARE IMAGE  ▼▼▼
#define THIS_BUD         BUD_RIGHT
```

Change `BUD_RIGHT` to `BUD_LEFT` for the left bud image. Everything else — key table, provisioning call, MAC arrays — follows automatically.

---

## Full Configuration Block

Located at the top of `board_jl7016g_hybrid_cfg.h` (BUD IDENTITY section, ~line 26):

```c
//*******************************************************************************//
//              BUD IDENTITY — SINGLE POINT OF CHANGE PER FIRMWARE BUILD          //
//                                                                                 //
//  Set THIS_BUD to BUD_RIGHT or BUD_LEFT. All downstream config follows.         //
//  BUD_RIGHT → key table: Hold=VolUp / DoubleTap=Next  / provisioning = B02 MAC  //
//  BUD_LEFT  → key table: Hold=VolDown/ DoubleTap=Prev / provisioning = B01 MAC  //
//                                                                                 //
//  Pair 1 MAC table (update here if hardware MACs change):                       //
//    B01 Left  EDR/TWS-local : 3C:00:0A:7E:1A:00                                 //
//    B02 Right EDR/TWS-local : 3C:00:0A:7E:1A:01                                 //
//    Common pair address     : AA:BB:CC:00:01:FF                                  //
//    TWS discovery pair code : 0x6688                                             //
//                                                                                 //
//  Provisioning call in user_cfg.c is automatic — no manual comment toggle.      //
//*******************************************************************************//
#define BUD_LEFT    0
#define BUD_RIGHT   1

// Pair 1 MAC addresses and pair code
#define P1_LEFT_MAC      {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x00}
#define P1_RIGHT_MAC     {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x01}
#define P1_COMMON_MAC    {0xAA, 0xBB, 0xCC, 0x00, 0x01, 0xFF}
#define P1_PAIR_CODE     0x6688

//  ▼▼▼  CHANGE ONLY THIS LINE PER FIRMWARE IMAGE  ▼▼▼
#define THIS_BUD         BUD_RIGHT

// Derived — consumed by key table and provisioning
#define TCFG_RIGHT_BUD   THIS_BUD
```

---

## How Each Define Is Used Downstream

### TCFG_RIGHT_BUD — key table (board_jl7016g_hybrid.c)

The board `.c` file uses `TCFG_RIGHT_BUD` to select which physical key performs which audio action:

| Value | Hold action | Double-tap action |
|---|---|---|
| `BUD_RIGHT` (1) | Volume Up | Next track |
| `BUD_LEFT` (0) | Volume Down | Previous track |

No change needed here — it reads `TCFG_RIGHT_BUD` which is now derived from `THIS_BUD`.

### TCFG_RIGHT_BUD — provisioning auto-select (user_cfg.c)

```c
// user_cfg.c — automatic, no manual toggle needed
#if TCFG_MANUAL_MAC_PROVISIONING_ENABLE
    // Automatic — driven by THIS_BUD in board_jl7016g_hybrid_cfg.h
    // Change only THIS_BUD there; no manual toggle needed here.
#if TCFG_RIGHT_BUD
    bt_provision_pair1_right_bud();
#else
    bt_provision_pair1_left_bud();
#endif
#endif
```

### P1_LEFT_MAC / P1_RIGHT_MAC / P1_COMMON_MAC / P1_PAIR_CODE — provisioning functions (user_cfg.c)

Both provisioning functions now use the defines instead of raw bytes:

```c
// bt_provision_pair1_left_bud()
u8 edr_mac[6]    = P1_LEFT_MAC;
u8 tws_local[6]  = P1_LEFT_MAC;
u8 tws_remote[6] = P1_RIGHT_MAC;    // sibling = right
u8 tws_common[6] = P1_COMMON_MAC;
u8 tws_channel   = BUD_LEFT;
u16 pair_code    = P1_PAIR_CODE;

// bt_provision_pair1_right_bud()
u8 edr_mac[6]    = P1_RIGHT_MAC;
u8 tws_local[6]  = P1_RIGHT_MAC;
u8 tws_remote[6] = P1_LEFT_MAC;     // sibling = left
u8 tws_common[6] = P1_COMMON_MAC;
u8 tws_channel   = BUD_RIGHT;
u16 pair_code    = P1_PAIR_CODE;
```

---

## Build Workflow — Left vs Right Image

### Right bud firmware (B02)

```c
#define THIS_BUD   BUD_RIGHT   // ← this line only
```

Build → flash → right bud.

- Key: Hold = Vol Up, Double-tap = Next
- EDR MAC: `3C:00:0A:7E:1A:01`
- TWS remote: `3C:00:0A:7E:1A:00` (left bud)
- Channel: 0x01

### Left bud firmware (B01)

```c
#define THIS_BUD   BUD_LEFT    // ← this line only
```

Build → flash → left bud.

- Key: Hold = Vol Down, Double-tap = Prev
- EDR MAC: `3C:00:0A:7E:1A:00`
- TWS remote: `3C:00:0A:7E:1A:01` (right bud)
- Channel: 0x00

---

## Changing MAC Addresses for a New Pair

If you add a second pair of buds (B03/B04), add new defines alongside the existing ones:

```c
// Pair 1 (B01/B02) — existing
#define P1_LEFT_MAC      {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x00}
#define P1_RIGHT_MAC     {0x3C, 0x00, 0x0A, 0x7E, 0x1A, 0x01}
#define P1_COMMON_MAC    {0xAA, 0xBB, 0xCC, 0x00, 0x01, 0xFF}
#define P1_PAIR_CODE     0x6688

// Pair 2 (B03/B04) — new
#define P2_LEFT_MAC      {0x3C, 0x00, 0x0A, 0x7E, 0x1B, 0x00}
#define P2_RIGHT_MAC     {0x3C, 0x00, 0x0A, 0x7E, 0x1B, 0x01}
#define P2_COMMON_MAC    {0xAA, 0xBB, 0xCC, 0x00, 0x02, 0xFF}
#define P2_PAIR_CODE     0x6688
```

Then duplicate the provisioning functions for pair 2 in user_cfg.c and call them via `THIS_PAIR` logic.

---

## What Was Changed

| File | Change |
|---|---|
| `board_jl7016g_hybrid_cfg.h` | Expanded BUD IDENTITY block: added `BUD_LEFT`, `BUD_RIGHT`, `THIS_BUD`, `P1_*` defines. `TCFG_RIGHT_BUD` is now derived from `THIS_BUD`. |
| `user_cfg.c` — provisioning call | Replaced manual comment/uncomment with `#if TCFG_RIGHT_BUD` auto-select. |
| `user_cfg.c` — `bt_provision_pair1_left_bud()` | Replaced raw byte arrays with `P1_LEFT_MAC`, `P1_RIGHT_MAC`, `P1_COMMON_MAC`, `P1_PAIR_CODE`, `BUD_LEFT`. |
| `user_cfg.c` — `bt_provision_pair1_right_bud()` | Replaced raw byte arrays with `P1_RIGHT_MAC`, `P1_LEFT_MAC`, `P1_COMMON_MAC`, `P1_PAIR_CODE`, `BUD_RIGHT`. |

---

## MAC Address Reference

| Label         | Address             | Role                                   |
| ------------- | ------------------- | -------------------------------------- |
| B01 Left EDR  | `3C:00:0A:7E:1A:00` | Left bud Bluetooth identity            |
| B02 Right EDR | `3C:00:0A:7E:1A:01` | Right bud Bluetooth identity           |
| Pair common   | `AA:BB:CC:00:01:FF` | Shared pair identity for TWS discovery |
| Pair code     | `0x6688`            | TWS discovery handshake code           |

---

## Related Documents

- [→ MAC ADDRESS MASTER LIST — 10 Buds 5 Pairs](MAC%20ADDRESS%20MASTER%20LIST%20-%2010%20Buds%205%20Pairs.md)
- [→ TWS SIBLING RECIPROCAL RELATIONSHIP](TWS%20SIBLING%20RECIPROCAL%20RELATIONSHIP%20-%20Configuration%20Guide.md)
- [→ SDK IMPLEMENTATION — Manual MAC Provisioning Functions](SDK%20IMPLEMENTATION%20-%20Manual%20MAC%20Provisioning%20Functions.md)
- [→ QUICK REFERENCE — user_cfg.c Provisioning Guide](QUICK%20REFERENCE%20-%20user_cfg.c%20Provisioning%20Guide.md)
- [→ TWS DEEP DIVE — Bud Identity, MAC Strategy](../DOC%20LIBRARY/TWS%20DEEP%20DIVE%20%E2%80%94%20Reconnect%20Lag%2C%20Bud%20Identity%2C%20MAC%20Strategy%2C%20and%20Risks.md)
