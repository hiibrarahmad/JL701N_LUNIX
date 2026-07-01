# Updated Log 2 - Left Bud Validation and Final Fix

## What This Log Confirms

From your latest capture:
- Manual provisioning function executed for LEFT bud.
- TWS local/remote/common/channel/pair-code writes are logged.
- TWS discovery uses expected `3C:00:0A:7E:1A:00` local and `...01` sibling.
- Phone link eventually connects and A2DP starts.

## Critical Observation in This Log

Although provisioning printed:
- `CFG_BT_MAC_ADDR (102) = 3C:00:0A:7E:1A:00`

Later it still printed:
- `[USER_CFG]mac:` then `BB 0A 2C 77 5B 37`
- `-----edr + ble 's address-----` also showed `BB 0A 2C 77 5B 37`

This means runtime EDR address still came from old BTIF value in that run.

## Why It Happened

Even after manual write calls, immediate readback path could still return old/random BTIF value during same boot window.

So the code was provisioning correctly, but runtime path was not enforcing the provisioned MAC strongly enough.

## Final Fix Applied (Now in SDK)

In `apps/earphone/user_cfg.c`:
1. Added manual MAC override buffer and valid flag.
2. Provision functions now store expected EDR MAC in override buffer.
3. `cfg_file_parse()` now enforces that MAC into runtime `mac_buf` and rewrites `CFG_BT_MAC_ADDR` during the same boot.

Result:
- Runtime `bt_cfg.mac_addr` will match selected manual profile in current boot.
- Debug log `mac:` should show the manual value, not fallback random.

## Line-by-Line Highlights (All Important Events Covered)

### Boot and clocks
- `[CLOCK]` and register dumps are normal bring-up telemetry.

### RTOS init
- `create_task` lines for `systimer`, `app_core`, idles, and `sys_event` are normal.
- `priority 6 reserved` warning is non-fatal.

### Storage and VM
- `sdfile mount succ` and `vm_info` indicate normal storage startup.

### USER_CFG load
- Names and RF load correctly.
- Pair code initially shows `FF FF` before manual hook runs (ordering artifact).

### Manual LEFT provisioning section
- `Provisioning Pair 1 - LEFT BUD (B01)` appears.
- Correct writes logged for IDs 102,95,96,97,98,602.
- Raw dumps show `3C..00` and common address `AA:BB:CC:00:01:FF`.

### Runtime MAC mismatch section in this log
- `[USER_CFG]mac:` still shows `BB 0A 2C 77 5B 37`.
- Confirms why final enforce patch was necessary.

### TWS operation
- `tws_task_init` shows left identity.
- Page/link sequences target sibling correctly.
- TWS connects and sync events fire (`LED/TONE/BAT sync`).

### BLE/RCSP churn
- `LL Adv already destroy` appears during adv state transitions, usually benign.
- `/config.dat Fail` repeated: optional config file missing in your package.

### Phone connection
- First attempt hits timeout and retries.
- Later authentication and encryption succeed.
- HFP setup and user confirmation events proceed.
- `BT_STATUS_CONNECTED` and `BT_STATUS_FIRST_CONNECTED` occur.

### Audio path
- Prompt decode warnings (`wtgv2_dec err:64`) reappear but not fatal.
- A2DP starts at end (`a2dp_media_type:AAC`) and DAC ramps to music mode.

## Work/Not-Work Verdict for This Specific Capture

### Working in this log
- Manual provisioning function execution: YES
- TWS pair mapping behavior: YES
- BLE/BR stack startup and phone profile connect: YES
- A2DP media start: YES

### Not fully working in this log
- Runtime EDR MAC selection consistency: NO (still showed fallback MAC)

### After final code fix (now applied)
- Runtime EDR MAC consistency should be YES on next boot.

## Next-Run Acceptance Criteria

On next left-bud boot, verify:
1. `Provisioning Pair 1 - LEFT BUD (B01)` appears.
2. `CFG_BT_MAC_ADDR ... 3C:00:0A:7E:1A:00` appears.
3. `[USER_CFG]mac:` prints `3C 00 0A 7E 1A 00`.
4. `-----edr + ble 's address-----` EDR line also prints `3C 00 0A 7E 1A 00`.

If all four pass, MAC implementation is fully correct in runtime and persistent path.

## PC5 Pull-Up/Pull-Down (Updated Project Requirement)

Current project rule:
- PC5 bias is required for stable/predictable TWS side behavior.
- Do not treat PC5 as optional in factory wiring and validation.
- Manual MAC provisioning does not replace hardware pin-state discipline.
