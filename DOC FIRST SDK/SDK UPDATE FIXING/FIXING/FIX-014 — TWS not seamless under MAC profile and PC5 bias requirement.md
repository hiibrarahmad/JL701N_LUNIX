---
tags: [fix, tws, mac-provisioning, pc5, stability]
date: 2026-04-28
status: IN PROGRESS
severity: BEHAVIORAL REGRESSION
---

# FIX-014 - TWS Not Seamless Under MAC Profile And PC5 Bias Requirement

## Summary

After manual MAC provisioning became functional, TWS operation is improved and mostly stable, but still not fully seamless in all transitions (role-switch, reconnect, adv churn windows).

In parallel, project policy is now explicit: PC5 must keep a defined hardware bias state for predictable left/right resolution and stable TWS behavior.

## Observed Behavior

1. Manual provisioning banners and MAC identity are correct in latest logs.
2. TWS links and phone links do establish.
3. Not-seamless points still appear:
- repeated adv enable/disable churn
- intermittent reconnect loops or temporary detach windows
- tone/volume sync bursts around role transitions

## Hardware Requirement (Mandatory)

PC5 must not float.

Required board-level policy:
- one bud uses PC5 pull-down (left resolution path under current channel mode)
- one bud uses PC5 pull-up (right resolution path)
- ensure both pulls are stable and validated at boot sampling moment

This requirement remains in effect even with manual MAC provisioning enabled.

## Why This Is In FIXING Folder

This is no longer only a provisioning note; it is a system-level behavior item involving:
- identity path (MAC/TWS IDs)
- side resolution path (PC5)
- runtime state-machine smoothness (TWS/ADV/audio transitions)

## Current Status

- MAC provisioning path: WORKING
- PC5 requirement: MANDATORY and retained
- TWS seamlessness: PARTIAL (still needs tuning)

## Next Actions

1. Add debounce/rate-limit for adv state toggles during TWS role transitions.
2. Review TWS event reason 7/10/12/13 sequence for unnecessary mode churn.
3. Keep PC5 pull hardware checklist as factory gate before RF debug.
4. Re-run long-duration soak with both buds and capture detach/retry statistics.

## Exit Criteria

This fix can move to VERIFIED when:
- TWS role transitions are smooth without repeated reconnect churn
- adv toggle storm is reduced to expected minimum
- no user-noticeable audio discontinuity during switch windows
- PC5 pull state validation passes on all production samples
