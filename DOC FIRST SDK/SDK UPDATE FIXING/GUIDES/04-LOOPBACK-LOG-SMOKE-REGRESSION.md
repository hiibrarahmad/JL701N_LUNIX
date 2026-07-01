---
tags: [guide, testing, loopback, tws, smoke-test, regression, uart-log]
status: active
owner: firmware
last_updated: 2026-05-19
---

# Loopback Log Smoke Regression Guide

## Objective
Run a repeatable no-code-change loop to:
1. Flash current firmware.
2. Capture right/left bud logs simultaneously.
3. Validate smoke and regression signals.
4. Record findings for TWS sibling reconnect behavior.

## Hardware/Port Map
- Right bud: COM4
- Left bud: COM25
- COM source: JLVirtual serial ports (JL updater environment)

## Current UART Baseline
Reference board config uses:
- [apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L46)
- Baud: 115200

## Flash Tool Entry Point
Existing flash script:
- [cpu/br28/tools/download/earphone/download_app_ota.bat](cpu/br28/tools/download/earphone/download_app_ota.bat)

## Test Toolkit
Toolkit folder:
- [tools/loopback_test](tools/loopback_test)

Primary scripts:
- [tools/loopback_test/run_loopback.ps1](tools/loopback_test/run_loopback.ps1)
- [tools/loopback_test/capture_dual_logs.py](tools/loopback_test/capture_dual_logs.py)
- [tools/loopback_test/analyze_smoke_regression.py](tools/loopback_test/analyze_smoke_regression.py)
- [tools/loopback_test/profiles/smoke_regression_default.json](tools/loopback_test/profiles/smoke_regression_default.json)

## Execution Steps
1. Open terminal at repo root.
2. Install dependency once:
   - pip install -r tools/loopback_test/requirements.txt
3. Run guided workflow:
   - powershell -ExecutionPolicy Bypass -File tools/loopback_test/run_loopback.ps1 -RightPort COM4 -LeftPort COM25 -Baud 115200 -CaptureSeconds 120
4. At prompt "DOWNLOAD mode": put board in download mode, then continue.
5. Flash with current method (no code modifications).
6. At prompt "LOG mode": switch buds to log mode, then continue.
7. Wait for capture + analysis to complete.

## Outputs
Stored under:
- [tools/loopback_test/logs](tools/loopback_test/logs)

Per run:
- loopback_merged_YYYYMMDD_HHMMSS.log
- right_YYYYMMDD_HHMMSS.log
- left_YYYYMMDD_HHMMSS.log
- loopback_merged_YYYYMMDD_HHMMSS.report.md

## Smoke/Regression Rules
Default profile result policy:
1. FAIL if any forbidden keyword appears (assert, panic, hardfault, fatal, watchdog, exception).
2. WARN if no TWS signal keyword appears.
3. PASS otherwise.

## TWS Reconnect Focus
For sibling-store reconnect checks, look for sequences containing:
- tws
- sibling
- pair
- connect
- reconnect

If PC5 pull/pull-down changes correlate with reconnect loss, annotate the report with:
1. Hardware state (PC5 pull-up, pull-down, floating).
2. Which bud failed to reconnect (COM4 right or COM25 left).
3. First error/warning line around reconnect attempt.

## Loopback Run Log Template
Copy into your daily note if needed:

- Firmware build ID/token:
- Flash success time:
- Right bud COM4 log seen: yes/no
- Left bud COM25 log seen: yes/no
- Pair result: pass/fail
- Sibling reconnect result: pass/fail
- Regression status: pass/warn/fail
- Notes:
