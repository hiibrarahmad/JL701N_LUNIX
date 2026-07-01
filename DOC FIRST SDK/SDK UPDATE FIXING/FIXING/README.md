---
tags: [index, fixing, overview, component-index]
date: 2026-05-05
---

# FIXING — Fix Records Index

**22 documented fixes** covering the full JL7016G Hybrid SDK bring-up and feature development cycle, from first build errors through to TWS per-bud key dispatch.

| Status                | Count       |
| --------------------- | ----------- |
| ✅ COMPLETE & DEPLOYED | 21          |
| ⏳ IN PROGRESS         | 1 (FIX-014) |

---

## Quick Navigation

> Not sure which fix applies to your problem? Use the tables below.
> - **By category** → find fixes related to a subsystem
> - **By file** → find every fix that touched a specific source file
> - **By symptom** → common error messages mapped to fix records

---

## Index by Category

### 🔨 Build & Linker Errors — FIX-001 to 003

| Fix | Title | Severity |
|-----|-------|----------|
| [FIX-001](./FIX-001%20—%20TCFG_IMU_SENSOR_PWR_PORT%20Undeclared.md) | `TCFG_IMU_SENSOR_PWR_PORT` undeclared identifier | ERROR — blocks build |
| [FIX-002](./FIX-002%20—%20lis2de12%20driver%20object%20missing%20at%20link.md) | lis2de12 driver object missing at link | ERROR — blocks link |
| [FIX-003](./FIX-003%20—%20undefined%20references%20online_db%20and%20fft_pca%20symbols.md) | Undefined references — `online_db`, FFT/PCA symbols | ERROR — blocks link |

### 📡 TWS (True Wireless Stereo) — FIX-004, 014, 020–022

| Fix                                                                                                         | Title                                                                 | Severity               | Status |
| ----------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | ---------------------- | ------ |
| [FIX-004](./FIX-004%20—%20TWS%20auto%20pairing%20and%20PC5%20channel%20select%20validation.md)              | TWS auto pairing + PC5 channel select validation                      | FUNCTIONAL BLOCKER     | ✅      |
| [FIX-014](./FIX-014%20—%20TWS%20not%20seamless%20under%20MAC%20profile%20and%20PC5%20bias%20requirement.md) | TWS not seamless under MAC profile + PC5 bias                         | BEHAVIORAL REGRESSION  | ⏳      |
| [FIX-020](./FIX-020%20—%20TWS%20Volume%20Desync%20Between%20Buds.md)                                        | TWS volume desync — slave key presses didn't sync to master           | BUG                    | ✅      |
| [FIX-021](./FIX-021%20—%20Per-Bud%20Key%20Table%20Split%20Does%20Not%20Work%20in%20TWS.md)                  | Compile-time per-bud key table splits are ineffective in TWS          | INVESTIGATION / DESIGN | ✅      |
| [FIX-022](./FIX-022%20—%20Right%20Bud%20Vol%20Up%20Left%20Bud%20Vol%20Down%20Channel-Aware%20Dispatch.md)   | Right bud Vol Up / Left bud Vol Down — runtime channel-aware dispatch | FEATURE                | ✅      |

### 🔵 Bluetooth / BLE Identity — FIX-005, 006

| Fix | Title | Severity |
|-----|-------|----------|
| [FIX-005](./FIX-005%20—%20BLE%20MAC%20Address%20Ignored%20at%20Boot.md) | BLE MAC address set in Config GUI never applied at boot | FUNCTIONAL BUG |
| [FIX-006](./FIX-006%20—%20Hardcoded%20Buddie%20Name%20Overwrites%20Config%20GUI%20Name.md) | Hardcoded "Buddie" name overwrites Config GUI device name | FUNCTIONAL BUG |

### 👆 LP Touch / PB4 / CTMU — FIX-007 to 010

| Fix | Title | Severity |
|-----|-------|----------|
| [FIX-007](./FIX-007%20—%20PB4%20gestures%20dropped%20on%20eartch%20reference%20channel.md) | PB4 gestures dropped on eartch reference channel | FUNCTIONAL BUG |
| [FIX-008](./FIX-008%20—%20CH3%20long%20hold%20suppressed%20by%20long-by-res%20gate.md) | CH3 long/hold suppressed by long-by-res gate | FUNCTIONAL BUG |
| [FIX-009](./FIX-009%20—%20PB4%20touch%20range%20rejected%20by%20low%20algorithm%20max.md) | PB4 touch range rejected by low algorithm max | FUNCTIONAL BUG |
| [FIX-010](./FIX-010%20—%20in-ear%20remap%20hook%20active%20while%20ear%20detect%20disabled.md) | In-ear remap hook active while ear-detect disabled | EVENT-ROUTING BUG |

### 🎙️ Microphone / Audio — FIX-012, 013

| Fix | Title | Severity |
|-----|-------|----------|
| [FIX-012](./FIX-012%20—%20MIC%20power%20PA0%20unconnected%20switched%20to%20PA2%20MICBIAS.md) | MIC power on PA0 unconnected — switched to PA2 MICBIAS | HARDWARE BRING-UP BLOCKER |
| [FIX-013](./FIX-013%20—%20MIC0%20differential%20mode%20mismatch%20changed%20to%20single-ended.md) | MIC0 differential mode mismatch — changed to single-ended | FUNCTIONAL — call MIC inaudible |

### 🔌 PB1 / PC3 / GPIO Feedback — FIX-015 to 019

| Fix | Title | Severity |
|-----|-------|----------|
| [FIX-015](./FIX-015%20—%20PB1_COMPLETE_SOLUTION.md) | PB1 complete solution — channel unblocking, threshold, sensitivity | CRITICAL |
| [FIX-016](./FIX-016%20—%20PB1%20PC3%20GPIO%20Touch%20Feedback.md) | PB1 → PC3 GPIO real-time touch feedback output | FEATURE |
| [FIX-017](./FIX-017%20—%20PB1%20Hold%20Power-Off%20Fix.md) | PB1 hold triggers power-off — `key_value` fix | BUG |
| [FIX-018](./FIX-018%20—%20PB1%20Key%20Events%20Suppressed%20GPIO%20Only.md) | PB1 key events suppressed — GPIO-only role | BUG |
| [FIX-019](./FIX-019%20—%20PC3%20Polarity%20Inverted%20(Active%20LOW).md) | PC3 output polarity inverted to active-LOW | CHANGE |

### 🔧 UART / Debug — FIX-011

| Fix | Title | Severity |
|-----|-------|----------|
| [FIX-011](./FIX-011%20—%20UART%20framing%20mismatch%20during%20touch%20bring-up.md) | UART framing mismatch during touch bring-up (wrong baud rate) | DEBUGGING BLOCKER |

---

## Index by Changed File

Use this table to find every fix that modified a specific source file.

| Source File | Fix Records |
|-------------|-------------|
| `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h` | FIX-001, FIX-012, FIX-013, FIX-015, FIX-016, FIX-021 |
| `apps/earphone/board/br28/board_jl7016g_hybrid.c` | FIX-017, FIX-021, FIX-022 |
| `cpu/br28/lp_touch_key.c` | FIX-007, FIX-008, FIX-009, FIX-015, FIX-016, FIX-018, FIX-019 |
| `apps/earphone/key_event_deal.c` | FIX-015, FIX-022 |
| `apps/earphone/bt_tws.c` | FIX-020 |
| `apps/earphone/app_main.c` | FIX-006 |
| `apps/earphone/user_cfg.c` | FIX-005, FIX-014 |
| Hardware / config-tool only (no C file change) | FIX-002, FIX-003, FIX-004, FIX-010, FIX-011 |

---

## Index by Symptom / Error Message

| Symptom or Error | Fix Record |
|-----------------|-----------|
| `'TCFG_IMU_SENSOR_PWR_PORT' undeclared` | [FIX-001](./FIX-001%20—%20TCFG_IMU_SENSOR_PWR_PORT%20Undeclared.md) |
| `undefined reference to 'lis2de12_...'` at link | [FIX-002](./FIX-002%20—%20lis2de12%20driver%20object%20missing%20at%20link.md) |
| `undefined reference to 'online_db'` or `'fft_pca'` | [FIX-003](./FIX-003%20—%20undefined%20references%20online_db%20and%20fft_pca%20symbols.md) |
| TWS pair won't connect / only one bud audible | [FIX-004](./FIX-004%20—%20TWS%20auto%20pairing%20and%20PC5%20channel%20select%20validation.md), [FIX-014](./FIX-014%20—%20TWS%20not%20seamless%20under%20MAC%20profile%20and%20PC5%20bias%20requirement.md) |
| BLE MAC address wrong / ignored | [FIX-005](./FIX-005%20—%20BLE%20MAC%20Address%20Ignored%20at%20Boot.md) |
| Device shows "Buddie" name regardless of Config GUI | [FIX-006](./FIX-006%20—%20Hardcoded%20Buddie%20Name%20Overwrites%20Config%20GUI%20Name.md) |
| PB4 touch detected in logs but no music/call action | [FIX-007](./FIX-007%20—%20PB4%20gestures%20dropped%20on%20eartch%20reference%20channel.md) |
| `CH3 long key by res` — long/hold never fires | [FIX-008](./FIX-008%20—%20CH3%20long%20hold%20suppressed%20by%20long-by-res%20gate.md) |
| `invalid touch value` for PB4 | [FIX-009](./FIX-009%20—%20PB4%20touch%20range%20rejected%20by%20low%20algorithm%20max.md) |
| Touch events intercepted by in-ear logic when disabled | [FIX-010](./FIX-010%20—%20in-ear%20remap%20hook%20active%20while%20ear%20detect%20disabled.md) |
| UART output shows garbage / `uuu` mixed with logs | [FIX-011](./FIX-011%20—%20UART%20framing%20mismatch%20during%20touch%20bring-up.md) |
| MIC produces zero audio / no signal | [FIX-012](./FIX-012%20—%20MIC%20power%20PA0%20unconnected%20switched%20to%20PA2%20MICBIAS.md) |
| MIC only picks up physical tap on capsule, not voice | [FIX-013](./FIX-013%20—%20MIC0%20differential%20mode%20mismatch%20changed%20to%20single-ended.md) |
| PB1 touch visible in logs but no app key events | [FIX-015](./FIX-015%20—%20PB1_COMPLETE_SOLUTION.md) |
| PB1 hold triggers power-off unexpectedly | [FIX-017](./FIX-017%20—%20PB1%20Hold%20Power-Off%20Fix.md) |
| PB1 touch triggers music play/pause/next | [FIX-018](./FIX-018%20—%20PB1%20Key%20Events%20Suppressed%20GPIO%20Only.md) |
| PC3 is HIGH when touched (expected LOW) | [FIX-019](./FIX-019%20—%20PC3%20Polarity%20Inverted%20(Active%20LOW).md) |
| Volume changes on one bud only — buds at different levels | [FIX-020](./FIX-020%20—%20TWS%20Volume%20Desync%20Between%20Buds.md) |
| `#if TCFG_RIGHT_BUD` key table split has no effect in TWS | [FIX-021](./FIX-021%20—%20Per-Bud%20Key%20Table%20Split%20Does%20Not%20Work%20in%20TWS.md) |
| Both buds do the same action (both Vol Up or both Next) | [FIX-022](./FIX-022%20—%20Right%20Bud%20Vol%20Up%20Left%20Bud%20Vol%20Down%20Channel-Aware%20Dispatch.md) |
| Volume oscillates up/down rapidly when holding touch | [FIX-022](./FIX-022%20—%20Right%20Bud%20Vol%20Up%20Left%20Bud%20Vol%20Down%20Channel-Aware%20Dispatch.md) |

---

## Status Legend

| Badge | YAML value | Meaning |
|-------|-----------|---------|
| ✅ | `COMPLETE & DEPLOYED` | Fix implemented, built, and in production firmware |
| ⏳ | `IN PROGRESS` | Partially resolved; known issues remain — see FIX record |
| ℹ️ | `DOCUMENTED ONLY` | Architectural finding recorded; no code change needed |

---

**Back to:** [→ Main Canvas](../MAIN%20CANVAS.canvas) | [→ FIXING Canvas](./00%20-%20FIXING.canvas)
