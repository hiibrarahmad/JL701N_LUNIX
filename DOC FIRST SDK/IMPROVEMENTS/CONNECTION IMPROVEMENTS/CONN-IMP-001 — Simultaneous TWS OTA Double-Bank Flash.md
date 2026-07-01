---
tags: [connection, ota, tws, flash, double-bank, firmware-update, jl7016g, improvement]
date: 2026-06-08
status: PLANNED — HARDWARE REQUIRED FIRST
effort: 🔴 High
risk: 🔴 Requires PCB flash chip upgrade from 1 MB to 2 MB
priority: 16 — High effort, critical for production OTA
---

# 📡 CONN-IMP-001 — Simultaneous TWS OTA (Double-Bank Flash)

> **One-line summary:** Currently OTA updates must be applied to each bud sequentially (left, then right). Enable double-bank flash (2 MB) to allow both buds to receive and apply the same firmware update simultaneously — the production-standard approach.

---

## Current State

Single-bank OTA only:

```c
// board_jl7016g_hybrid_global_build_cfg.h
#define CONFIG_DOUBLE_BANK_ENABLE    0     // double-bank disabled
#define CONFIG_FLASH_SIZE            FLASH_SIZE_1M   // 1 MB flash

// board_jl7016g_hybrid_cfg.h
#define OTA_TWS_SAME_TIME_ENABLE     0     // simultaneous TWS OTA off
```

### Current OTA Flow (Single-Bank)

```
Phone BLE → left bud receives new firmware
         → left bud writes to single flash partition
         → left bud reboots with new firmware ✓
         → phone manually initiates OTA to right bud
         → right bud writes and reboots ✓
```

Problems:
- User must OTA each bud separately (poor UX)
- Window where left bud has new firmware but right has old — potential incompatibility
- If right-bud OTA fails, the pair has mismatched firmware

---

## What Double-Bank Enables

With 2 MB flash partitioned into two 1 MB banks:

```
Bank 0 (0x00000–0xFFFFF): Running firmware (1 MB)
Bank 1 (0x100000–0x1FFFFF): OTA staging area (1 MB)
```

### Simultaneous OTA Flow

```
Phone BLE → left bud downloads firmware to Bank 1
          ↓  (TWS link)
          → right bud receives same firmware via TWS from left
          → both buds write to Bank 1 simultaneously
          → both buds swap Bank 0 ↔ Bank 1 atomically
          → both reboot with new firmware at the same time ✓
```

Both buds are always on the same firmware version. Failed OTA = both remain on old version (safe rollback).

---

## Required Changes

### 1. PCB Hardware Change

Replace the current 1 MB SPI flash with a **2 MB SPI flash** (same footprint, compatible pinout).

Compatible flash alternatives (SOP-8, 3.3V, SPI):
| Part | Size | Package | Voltage | Compatible |
|---|---|---|---|---|
| GD25Q16 (current equivalent) | 2 MB | SOP-8 | 3.3V | ✅ |
| W25Q16JV | 2 MB | SOP-8 | 3.3V | ✅ |
| MX25L1606E | 2 MB | SOP-8 | 3.3V | ✅ |

All are pin-compatible with the current 1 MB flash — only BOM change, no PCB trace change.

### 2. Firmware Config Changes

```c
// board_jl7016g_hybrid_global_build_cfg.h
#define CONFIG_DOUBLE_BANK_ENABLE    1               // was 0
#define CONFIG_FLASH_SIZE            FLASH_SIZE_2M   // was FLASH_SIZE_1M

// board_jl7016g_hybrid_cfg.h
#define OTA_TWS_SAME_TIME_ENABLE     1               // was 0
```

### 3. Flash Layout Update (isd_config.ini)

The ISD config must be updated to reflect 2 MB flash and the new partition layout:

```ini
; cpu/br28/tools/isd_config.ini — update flash size
FLASH_SIZE = 0x200000       ; was 0x100000 (1 MB → 2 MB)
; Bank boundaries set by SDK toolchain automatically when DOUBLE_BANK_ENABLE=1
```

---

## ANC Coefficient Storage

Current ANC coefficient addresses in `isd_config.ini`:
```
ANCIF_ADR:  0xFD000
ANCIF1_ADR: 0xFD100
```
In the 2 MB layout these addresses shift — the SDK toolchain recalculates them automatically when `FLASH_SIZE_2M` is set. Verify the new addresses in the generated `.map` file before flashing.

---

## Additional Benefit — Space for LC3 and Future Features

2 MB flash also unblocks [AUDIO-IMP-007 LC3 Codec](../AUDIO%20IMPROVEMENTS/AUDIO-IMP-007%20—%20LC3%20Codec%20LE%20Audio.md) and provides room for:
- More tone files (currently limited by 1 MB)
- Larger ANC coefficient sets
- Additional BT profiles (PBAP, SPP)

---

## Risk & Trade-offs

| Aspect | Assessment |
|---|---|
| PCB change | BOM only — same SOP-8 footprint, direct substitution |
| Firmware regression | Test single-bud OTA (old flow) disabled; TWS OTA is the only path |
| OTA failure recovery | Double-bank is inherently safer — failed update = stay on Bank 0 |
| ANC coefficient migration | Addresses shift — re-flash ANC calibration data after upgrade |
| Cost | +~$0.05 per unit for 2 MB vs 1 MB flash |

---

## Implementation Sequence

1. 🔧 Source 2 MB compatible flash (GD25Q16 or W25Q16JV)
2. 🔧 Solder on dev board — verify basic boot (UART log should show 2 MB detected)
3. 🔧 Update firmware config flags
4. 🔧 Update `isd_config.ini` flash size
5. 🔧 Build and flash initial firmware to Bank 0
6. 🧪 Trigger OTA from JL earphone app → verify both buds update simultaneously
7. 🧪 Power cycle — confirm both buds on new firmware version

---

## Related
- [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md) — Section 5
- [→ AUDIO-IMP-007 LC3 Codec](../AUDIO%20IMPROVEMENTS/AUDIO-IMP-007%20—%20LC3%20Codec%20LE%20Audio.md) — Also requires 2 MB flash
- [→ MAC ADDRESS PROVISIONING](../../SDK%20UPDATE%20FIXING/UPDATE/MAC%20ADDRESS%20PROVISIONING/) — Flash layout changes affect MAC region too
- [→ FIX-005 BLE MAC Address](../../SDK%20UPDATE%20FIXING/FIXING/FIX-005%20—%20BLE%20MAC%20Address%20Ignored%20at%20Boot.md)
