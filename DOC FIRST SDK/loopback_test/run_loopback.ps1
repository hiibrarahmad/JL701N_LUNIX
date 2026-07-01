param(
    [string]$RightPort = "COM4",
    [string]$LeftPort = "COM25",
    [int]$Baud = 115200,
    [int]$CaptureSeconds = 120,
    [string]$ExpectedFirmwareToken = ""
)

Write-Host "============================================="
Write-Host "Loopback Smoke/Regression Test Runner"
Write-Host "Right bud: $RightPort | Left bud: $LeftPort | Baud: $Baud"
Write-Host "============================================="

Write-Host "Step 1: Put board in DOWNLOAD mode, then press Enter to continue flashing prompt."
Read-Host | Out-Null

Write-Host "Flashing firmware using cpu/br28/tools/download/earphone/download_app_ota.bat"
Push-Location cpu/br28/tools/download/earphone
cmd /c download_app_ota.bat
$flashExit = $LASTEXITCODE
Pop-Location

if ($flashExit -ne 0) {
    Write-Error "Firmware flash failed with exit code $flashExit"
    exit $flashExit
}

Write-Host "Flash complete."

Write-Host "Step 2: Put both buds in LOG mode (JLVirtual serial ready), then press Enter."
Read-Host | Out-Null

python tools/loopback_test/capture_dual_logs.py --right-port $RightPort --left-port $LeftPort --baud $Baud --duration $CaptureSeconds
if ($LASTEXITCODE -ne 0) {
    Write-Error "Log capture failed"
    exit $LASTEXITCODE
}

$latestLog = Get-ChildItem tools/loopback_test/logs/loopback_merged_*.log |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $latestLog) {
    Write-Error "No merged log found in tools/loopback_test/logs"
    exit 3
}

python tools/loopback_test/analyze_smoke_regression.py --log $latestLog.FullName --expected-fw-token $ExpectedFirmwareToken
exit $LASTEXITCODE
