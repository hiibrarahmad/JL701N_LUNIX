---
tags: [fix, uart, logging, terminal, bring-up]
date: 2026-04-27
status: COMPLETE & DEPLOYED
severity: DEBUGGING BLOCKER
---

# FIX-011 — UART Framing Mismatch During Touch Bring-Up

## Summary

During LP touch and in-ear bring-up, UART output showed mixed readable logs and garbage characters (`uuu`, random symbols), making diagnosis unreliable.

## Root Cause

Firmware UART output was active, but host-side terminal framing/settings were inconsistent.

## Fix Applied

Standardized UART bring-up settings:

- baud: `115200`
- frame: `8N1`
- flow control: disabled
- board TX: `PB5`

Confirmed logging tags used during validation:

- `[LP_KEY]`
- `[EARTCH_EVENT_DEAL]`
- `key_event:`

## Related Documentation

- `DOC FIRST SDK/SDK UPDATE FIXING/UPDATE/DOC LIBRARY/UART LOGGING NOTE — Touch Bring-up, Pin, Baud, and Terminal Setup.md`

## Verification

- Stable readable logs with correct terminal framing.
- UART logs were sufficient to isolate event-routing defects in touch/in-ear path.
