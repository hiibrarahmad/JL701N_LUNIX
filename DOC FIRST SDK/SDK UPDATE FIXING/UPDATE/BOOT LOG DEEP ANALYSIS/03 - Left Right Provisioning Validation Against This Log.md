# Left Right Provisioning Validation Against This Log

## Your Question

You flashed left then right configuration and asked if it is really working.

## Verdict for This Specific Capture

Based on the provided log, your intended manual Pair 1 identity is **not** active in this run.

### Evidence

1. Pair code read:
- `[USER_CFG]tws pair code config:` then `FF FF`
- Expected for Pair 1 manual setup: `0x6688`

2. EDR MAC in runtime:
- `[USER_CFG]mac:` then `BB 0A 2C 77 5B 37`
- Expected left/right: `3C:00:0A:7E:1A:00` or `3C:00:0A:7E:1A:01`

3. Later address dump confirms same active address:
- `-----edr + ble 's address-----`
- `BB 0A 2C 77 5B 37`

So this run used fallback/random identity path.

## Why It Happened

In your SDK revision at time of capture, manual provisioning guard/macro placement caused provisioning branch to be inactive during `cfg_file_parse()`.

That has now been corrected by placing provisioning macro definition before `cfg_file_parse()` and keeping provisioning calls in the active block.

## What “Working” Looks Like Next Boot

For LEFT build boot log should show:
- `Provisioning Pair 1 - LEFT BUD (B01)`
- `CFG_BT_MAC_ADDR (102) = 3C:00:0A:7E:1A:00`
- `CFG_TWS_LOCAL_ADDR (95) = 3C:00:0A:7E:1A:00`
- `CFG_TWS_REMOTE_ADDR (96) = 3C:00:0A:7E:1A:01`
- `CFG_TWS_PAIR_CODE_ID (602) = 0x6688`

For RIGHT build boot log should show:
- `Provisioning Pair 1 - RIGHT BUD (B02)`
- `CFG_BT_MAC_ADDR (102) = 3C:00:0A:7E:1A:01`
- `CFG_TWS_LOCAL_ADDR (95) = 3C:00:0A:7E:1A:01`
- `CFG_TWS_REMOTE_ADDR (96) = 3C:00:0A:7E:1A:00`
- `CFG_TWS_PAIR_CODE_ID (602) = 0x6688`

And later:
- `[USER_CFG]mac:` must print the same provisioned MAC, not random.
- `tws pair code config` must not be `FF FF`.

## Flash Order and Build Discipline (Critical)

Use two separate firmware binaries:
1. LEFT build: only left provisioning function enabled
2. RIGHT build: only right provisioning function enabled

Do not flash same binary to both buds.

## Pass/Fail Checklist

PASS when all true:
- Left and right each log their own provisioning banner
- Pair code resolves to 0x6688 on both
- Reciprocal sibling addresses are correct
- TWS connects without long retry loops

FAIL when any true:
- Pair code still `FF FF`
- Runtime MAC is random/non-target
- Both buds show same local MAC

## Current Status in Your Shared Log

- Boot: PASS
- TWS eventually connects: PASS (with retries)
- Manual identity provisioning: FAIL for this capture
- Action required: reflash after corrected macro/order fix, then verify boot signatures above
