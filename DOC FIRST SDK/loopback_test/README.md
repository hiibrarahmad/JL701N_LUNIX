# Loopback Test Toolkit

This folder provides a no-firmware-modification workflow for dual-bud loopback log testing.

## Bud/COM Mapping
- Right bud: COM4
- Left bud: COM25

## Files
- capture_dual_logs.py: captures live logs from both COM ports and stores merged + per-bud logs.
- analyze_smoke_regression.py: evaluates a captured merged log for smoke/regression signals.
- run_loopback.ps1: guided runner that prompts for DOWNLOAD mode and LOG mode transitions.
- profiles/smoke_regression_default.json: default keyword profile.

## Setup
1. Install Python 3.10+.
2. Install dependencies:
   pip install -r tools/loopback_test/requirements.txt

## Typical Run
1. Start guided run:
   powershell -ExecutionPolicy Bypass -File tools/loopback_test/run_loopback.ps1 -RightPort COM4 -LeftPort COM25 -Baud 115200 -CaptureSeconds 120
2. Follow prompts:
   - Put board in DOWNLOAD mode for flashing.
   - Flash using your existing SDK script/tool.
   - Put buds in LOG mode.
3. Review outputs in tools/loopback_test/logs.

## Manual Commands
Capture only:
python tools/loopback_test/capture_dual_logs.py --right-port COM4 --left-port COM25 --baud 115200 --duration 120

Analyze only:
python tools/loopback_test/analyze_smoke_regression.py --log tools/loopback_test/logs/loopback_merged_YYYYMMDD_HHMMSS.log

## Output
- loopback_merged_*.log: merged time-ordered log from both buds.
- right_*.log: right bud raw stream.
- left_*.log: left bud raw stream.
- loopback_merged_*.report.md: smoke/regression report.
