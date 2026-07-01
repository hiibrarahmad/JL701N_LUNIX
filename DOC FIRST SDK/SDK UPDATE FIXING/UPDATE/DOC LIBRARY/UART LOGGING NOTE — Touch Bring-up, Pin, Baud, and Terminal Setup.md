# UART LOGGING NOTE — Touch Bring-up, Pin, Baud, and Terminal Setup

## Purpose

This note documents the UART logging setup used while bringing up LP touch and in-ear detection on the JL7016G hybrid board.

---

## Current UART Logging Setup

Configured in:

- `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h`

Current values:

- UART enabled: `TCFG_UART0_ENABLE = ENABLE_THIS_MOUDLE`
- TX pin: `PB5`
- RX pin: disabled / not used for print-only logging
- baudrate: `115200`

---

## Why UART Was Important Here

UART was enabled and used to confirm:

- touch channel transitions
- ear in / ear out state changes
- whether touch channels were incorrectly generating normal key events
- whether debug logs from the in-ear event handler were reaching the console

---

## Debug Logging Enabled In Code

The following debug outputs were enabled during bring-up:

- `cpu/br28/lp_touch_key.c`
  - `LOG_DEBUG_ENABLE`
- `apps/earphone/eartch_event_deal.c`
  - `LOG_DEBUG_ENABLE`
- `apps/earphone/log_config/app_config.c`
  - `log_tag_const_d_EARTCH_EVENT_DEAL = TRUE`

Expected tags on UART:

- `[LP_KEY]`
- `[EARTCH_EVENT_DEAL]`

---

## Correct Serial Terminal Settings

Use exactly:

- 115200 baud
- 8 data bits
- no parity
- 1 stop bit
- no flow control

Short form:

- `115200 8N1`

---

## Cause Of Garbled Logs Observed Earlier

The log stream showed valid debug lines mixed with garbage characters like:

- `FFFFFFFF`
- `xxx`
- `uuu`

This pattern means the UART text stream was partially valid but serial framing at the host side was wrong.

Most likely causes:

1. parity was set incorrectly, such as even parity
2. stop bits were wrong
3. flow control was enabled in terminal software
4. host was attached to the wrong TX pin

Because readable `[Info]`, `[Debug]`, and timestamped logs were present, the firmware side was already transmitting real text. That strongly indicates the main remaining issue was terminal configuration, not total UART failure.

---

## Practical Bring-up Checklist

1. connect UART TX from board `PB5` to USB-UART RX
2. connect GND to GND
3. open terminal at `115200 8N1`
4. disable hardware/software flow control
5. power cycle board
6. verify boot logs appear as readable ASCII
7. touch PB1 and watch `[LP_KEY]` and `[EARTCH_EVENT_DEAL]`

---

## What UART Helped Prove In This Task

UART logs helped prove:

1. touch detection was alive
2. CH3 long-click events were leaking through as normal key behavior
3. in-ear transitions were being generated
4. the interference problem was in event routing, not only in hardware sensing

That directly led to the driver fix where ear-detect channels were reserved from normal key event delivery.

---

## Recommendation

Keep UART logging enabled until:

- wear detect is fully stable
- touch feedback behavior is finalized
- false trigger rate is acceptable on real hardware

After that, debug verbosity can be reduced for production builds.

---

## Related FIX Records

| Fix | Title | Relevance |
|-----|-------|-----------|
| [FIX-011](../../FIXING/FIX-011%20—%20UART%20framing%20mismatch%20during%20touch%20bring-up.md) | UART framing mismatch during touch bring-up | Baud rate / terminal config fix |