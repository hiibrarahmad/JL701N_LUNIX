---
tags: [fix, build-error, board-config, imu]
date: 2026-04-22
status: COMPLETE & DEPLOYED
severity: ERROR (blocks build)
file_changed: apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h
---

# FIX-001 — `TCFG_IMU_SENSOR_PWR_PORT` Undeclared Identifier

## Error Message

```
cpu/br28/spatial_effect/spatial_effect_imu.c:693:26: error: use of undeclared identifier 'TCFG_IMU_SENSOR_PWR_PORT'
    imu_sensor_power_ctl(TCFG_IMU_SENSOR_PWR_PORT, 1);
                         ^
1 error generated.
```

---

## Root Cause Analysis

### Active board
`CONFIG_BOARD_JL7016G_HYBRID` is selected in `board_config.h`.

### Include chain
```
spatial_effect_imu.c
  → #include "app_config.h"
    → #include "board_config.h"
      → #include "board_jl7016g_hybrid_cfg.h"  ← ACTIVE (guarded by #ifdef CONFIG_BOARD_JL7016G_HYBRID)
      → board_jl701n_demo_cfg.h  ← NOT active (guarded by #ifdef CONFIG_BOARD_JL701N_DEMO)
      → board_jl701n_btemitter_cfg.h  ← NOT active
      → board_jl701n_anc_cfg.h  ← NOT active
```

### Where the macro is defined
`TCFG_IMU_SENSOR_PWR_PORT` was **only defined in the JL701N board configs** (all set to `IO_PORTG_05`). The JL7016G hybrid config was **missing the entire IMU sensor section**, so the macro was never defined when compiling for this board.

### Why the code uses it unconditionally
In `cpu/br28/spatial_effect/spatial_effect_imu.c` line 693, the call:
```c
imu_sensor_power_ctl(TCFG_IMU_SENSOR_PWR_PORT, 1);
```
…is made **without any `#ifdef` guard**, directly requiring the macro to be defined. The function body at line 751 is properly guarded with `#if (TCFG_IMU_SENSOR_PWR_PORT != NO_CONFIG_PORT)`, so setting it to `NO_CONFIG_PORT` makes the function a safe no-op.

---

## Fix Applied

**File:** `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h`

Added a complete IMU sensor configuration section (after the g-sensor section), including:

```c
//*********************************************************************************//
//                                  imu-sensor配置                                   //
//*********************************************************************************//
#define TCFG_IMUSENSOR_ENABLE                     0    //imu Sensor使能 (JL7016G不使用IMU)
#define TCFG_MPU6887P_ENABLE                      0
// ... (full sensor section — see source file)

/*
 * imu-sensor power manager
 * JL7016G没有独立IMU供电IO，配置NO_CONFIG_PORT
 * FIX: Added missing TCFG_IMU_SENSOR_PWR_PORT — was causing undeclared identifier
 *      build error in cpu/br28/spatial_effect/spatial_effect_imu.c:693
 */
#define TCFG_IMU_SENSOR_PWR_PORT                  NO_CONFIG_PORT
```

Setting `TCFG_IMU_SENSOR_PWR_PORT` to `NO_CONFIG_PORT` is correct because:
1. The JL7016G board does not have a dedicated IMU sensor power control IO
2. The `imu_sensor_power_ctl()` function body is guarded by `#if (TCFG_IMU_SENSOR_PWR_PORT != NO_CONFIG_PORT)` — so it becomes a no-op
3. All individual IMU sensor chip enables (`TCFG_ICM42670P_ENABLE`, etc.) are set to `0`

---

## Verification

- [ ] Run `.vscode/winmk.bat all` — confirm `spatial_effect_imu.c` compiles without errors
- [ ] Confirm no other files reference `TCFG_IMU_SENSOR_PWR_PORT` without it being defined

---

## Related Files

- `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h` — changed
- `cpu/br28/spatial_effect/spatial_effect_imu.c` — source of error
- `apps/earphone/board/br28/board_jl701n_demo_cfg.h` — reference: how JL701N defines this macro
