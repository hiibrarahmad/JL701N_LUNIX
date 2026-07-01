---
tags: [fix, tws, hardware, channel-select, validation]
date: 2026-04-22
status: COMPLETE & DEPLOYED
severity: FUNCTIONAL BLOCKER (TWS bring-up)
---

# FIX-004 — TWS Auto Pairing And PC5 Channel Select Validation

## Summary

TWS auto mode was configured correctly, but real-board pairing only succeeded after hardware channel split was applied on `PC5`.

## Verified Configuration Basis

From code/config:
- `TCFG_USER_TWS_ENABLE = 1`
- `CONFIG_TWS_PAIR_MODE = CONFIG_TWS_PAIR_BY_AUTO`
- `CONFIG_TWS_CHANNEL_SELECT = CONFIG_TWS_EXTERN_DOWN_AS_LEFT`
- `CONFIG_TWS_CHANNEL_CHECK_IO = IO_PORTC_05`

## Root Cause (Verified On Hardware)

With `CONFIG_TWS_EXTERN_DOWN_AS_LEFT`, local L/R side is decided by the sampled level on `PC5` at boot.

Effective behavior:
- `PC5` low -> local channel `'L'`
- `PC5` high -> local channel `'R'`

Using the same firmware on both boards is expected in this mode. The required difference is hardware level on `PC5` so each ear resolves a different side.

## Real-Board Validation Result

- Same firmware image uploaded to both boards.
- Initial state (without proper channel split): TWS did not form.
- Working state after hardware split:
  - Board A: `PC5` pull-down
  - Board B: `PC5` pull-up
- Result: TWS auto pairing formed and operation was confirmed.

## Why This Is Important

This project is configured for hardware-defined side detection, not separate left/right firmware variants. If both boards read the same `PC5` level, TWS pairing may fail or be unstable.

## Recommendation

For production and bring-up checklists:
- Verify `PC5` level mapping per board assembly.
- Ensure one unit resolves `'L'` and the other resolves `'R'` under the selected channel mode.
- Keep this check ahead of RF/link debugging to avoid false software root-cause assumptions.
