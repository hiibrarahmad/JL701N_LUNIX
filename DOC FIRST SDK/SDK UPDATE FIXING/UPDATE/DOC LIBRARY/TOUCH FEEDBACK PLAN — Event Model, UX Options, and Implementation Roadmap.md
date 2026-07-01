# TOUCH FEEDBACK PLAN — Event Model, UX Options, and Implementation Roadmap

## Goal

Build a clear touch interaction plan for the current JL7016G hybrid earphone setup so touch is predictable, debuggable, and easy to expand.

This plan is based on the current SDK state:

- LP touch / CTMU is enabled
- PB1 is the primary active touch channel
- PB4 is used as reference for in-ear detection stability
- PB1 is currently also used in a single-touch fallback model for in-ear state
- UART debug for touch and in-ear handling is enabled

---

## Current Touch Architecture

### Hardware Layer

The SDK uses the BR28 low-power CTMU touch engine.

Current board configuration:

- PB1 = touch channel 1 = primary active channel
- PB4 = touch channel 3 = reference channel for in-ear detection

Configured in:

- `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h`

### Driver Layer

The touch driver lives in:

- `cpu/br28/lp_touch_key.c`

It supports these raw event types:

- falling
- raising
- short click
- long click
- hold click
- short-click counting for double/triple/fourth/fifth clicks
- slide events when multiple channels are used as a slide surface

### App Layer

Normal key behavior is handled in:

- `apps/earphone/key_event_deal.c`

That file converts touch key events into product functions such as:

- play / pause
- previous / next track
- volume up / down
- call answer / hangup
- power off
- low latency toggle or other custom actions depending on key table mapping

### In-Ear Layer

Wear detection is handled by:

- `cpu/br28/lp_touch_key.c`
- `apps/earphone/eartch_event_deal.c`

Current logic now does two things:

1. differential ear-detect support using PB1 + PB4
2. single-touch fallback behavior on PB1:
   - press / hold => in-ear
   - release => out-ear

Current resolved behavior:

- PB1 (primary eartch channel) stays reserved for ear-detect flow.
- PB4 (reference eartch channel) is now allowed to emit normal key events via board-controlled macro.

---

## How Touch Works In This SDK

### 1. CTMU Detects Channel Activity

The hardware reports channel state changes and raw capacitance response values.

Important concepts:

- `FALLING` usually means touch/contact starts
- `RAISING` usually means touch/contact ends
- `LONG` / `HOLD` are time-derived events after sustained touch
- raw response values are used to reject false long-presses and to improve stability

### 2. Driver Decides Event Type

`lp_touch_key.c` evaluates timing and capacitance response to classify the touch into:

- click
- double click
- triple click
- long press
- hold
- release

### 3. Driver Sends Or Blocks The Event

The helper `__ctmu_notify_key_event()` is the gatekeeper.

In the current setup:

- PB1 is blocked from normal key delivery when used as primary ear-detect channel.
- PB4 can be used for normal gesture control even while acting as eartch reference channel.
- this is controlled by `TCFG_LP_EARTCH_REF_KEY_EVENT_ENABLE`.

### 4. App Maps Events To User Functions

`key_event_deal.c` turns logical key events into product behavior:

- music control
- call control
- power control
- volume control

This means touch functionality is a combination of:

- board config
- driver classification
- app-level event mapping

---

## Possible Touch Functionality We Can Build

### Category A — Media Control

Possible functions:

- single tap: play / pause
- double tap: next track
- triple tap: previous track
- long press: voice assistant or mode change
- hold: volume up or volume down

Notes:

- best when touch channel is dedicated to user input
- not ideal on PB1 right now if PB1 remains tied to in-ear detection

### Category B — Call Control

Possible functions:

- single tap: answer call
- long press: reject call
- double tap: hang up
- hold: switch call route or mute toggle

### Category C — Power / System Control

Possible functions:

- long hold: power off
- multi-click: low-latency mode
- multi-click: ANC mode cycle
- multi-click: TWS role test or engineering actions

### Category D — Feedback / UX

Possible feedback outputs:

- tone beep on touch accepted
- tone on mode switch
- voice prompt for ANC / EQ / game mode
- LED pulse when touch detected
- silent haptic-style behavior using audio cues only

### Category E — Wear / Presence Logic

Possible functions:

- pause music when removed
- resume when worn
- route call audio to phone when out of ear
- restore call audio to earbud when worn
- ignore key actions when earbud is not worn

### Category F — Gesture Extensions

If more channels are exposed later:

- slide up / slide down for volume
- left / right surface gestures
- separate function per earbud side
- touch + wear combined logic

---

## What Is Realistically Best For This Board Right Now

Because PB1 is already serving as the practical active touch point and PB4 is mainly a reference path, the most stable near-term design is:

### Recommended Phase 1

- Keep PB1 dedicated to wear-detect style touch state
- Use press / hold as "in-ear"
- Use release as "out-ear"
- Do not attach normal media key events to PB1 yet
- Keep PB4 as reference-only channel

Why:

- simplest behavior
- easiest to debug
- avoids accidental media/volume operations
- matches the current code changes already applied

### Recommended Phase 2

After wear-detect is stable:

- choose whether PB1 should remain wear-only
- or split behavior by context:
  - worn state active => media touch enabled
  - not worn => touch ignored

This phase needs deliberate UX design because one channel doing both wear detection and user command input can become noisy.

### Recommended Phase 3

If another real touch surface becomes available:

- dedicate PB1/PB4 to wear detection only
- dedicate new touch channel to user actions

This is the cleanest production design.

---

## Solid Implementation Plan

## Phase 1 — Stabilize Touch As Wear Input

Objective:

- reliable in-ear / out-ear behavior
- no unintended volume/playback changes

Tasks:

1. keep PB1/PB4 blocked from normal key event delivery
2. keep single-touch fallback active on PB1
3. verify UART logs show clean state transitions
4. tune thresholds and sensitivity only after behavior is stable

Success criteria:

- hold PB1 => stable in-ear event
- release PB1 => stable out-ear event
- no CH1/CH3 normal media action leaks

## Phase 2 — Add Touch Feedback

Objective:

- make touch feel intentional to the user

Tasks:

1. add tone when PB1 enters in-ear state
2. add tone or prompt when PB1 exits in-ear state if desired
3. optionally add LED pulse on valid touch recognition
4. document all feedback rules so they stay consistent

Success criteria:

- user can hear/see when touch is accepted
- no repeated noisy feedback while holding

## Phase 3 — Add Context-Aware Touch Actions

Objective:

- use touch for actual control without breaking wear detect

Candidate models:

1. worn-only media control
2. long-hold reserved for wear detect, click reserved for media
3. separate single-tap and hold timing windows

Recommended first experiment:

- click => play/pause only when already in-ear
- hold => preserve wear state logic

Risk:

- mixed-use on one channel can cause user confusion if timing is too sensitive

## Phase 4 — Production Tuning

Objective:

- turn prototype behavior into shippable UX

Tasks:

1. tune PB1 sensitivity
2. tune PB4 reference stability
3. reduce false positives from moisture / finger hover
4. reduce false negatives during light touch
5. finalize tone behavior and event timing

---

## UART Debugging Note

UART logging is now part of the touch bring-up workflow.

Current logging status:

- touch driver debug enabled
- in-ear event debug enabled
- app log config allows debug output for in-ear module

Use UART to validate:

- falling / raising transitions
- long-click or hold timing
- in-ear and out-ear state changes
- whether normal key events are being blocked correctly

Serial terminal requirements:

- baud: 115200
- data bits: 8
- parity: none
- stop bits: 1
- flow control: none

If garbage appears:

- terminal settings are wrong, especially parity/stop bits
- or the host is attached to the wrong TX pin

Current TX pin for logs:

- PB5

---

## Touch Feedback Options Matrix

| Function | Feasible Now | Risk | Notes |
|----------|--------------|------|-------|
| Wear detect on hold/release | Yes | Low | Already close to working model |
| Play/pause on tap | Possible | Medium | Only after wear path is stable |
| Volume on hold | Possible | High | Can conflict with wear timing |
| Next/prev on multi-click | Possible | Medium | Needs dedicated UX timing |
| Call answer/hangup | Possible | Medium | Good context-specific option |
| Slide volume control | Not now | Low | Needs more exposed touch channels |
| LED feedback | Possible | Low | Good next-step UX improvement |
| Voice prompt feedback | Possible | Low | Easy once event behavior is stable |

---

## Recommended Next Engineering Step

Implement touch feedback first, not more gestures.

Best immediate sequence:

1. verify PB1 hold/release wear transitions on hardware
2. add one short tone for valid in-ear entry
3. add one optional out-ear tone if it does not annoy the user
4. only then consider adding media control on touch

This keeps the design stable and avoids mixing too many responsibilities into one touch channel too early.

---

## Related FIX Records

| Fix | Title | Relevance |
|-----|-------|-----------|
| [FIX-016](../../FIXING/FIX-016%20—%20PB1%20PC3%20GPIO%20Touch%20Feedback.md) | PB1 → PC3 GPIO real-time touch feedback | GPIO feedback implementation |
| [FIX-018](../../FIXING/FIX-018%20—%20PB1%20Key%20Events%20Suppressed%20GPIO%20Only.md) | PB1 key events suppressed — GPIO only | PB1 role: GPIO output only |
| [FIX-019](../../FIXING/FIX-019%20—%20PC3%20Polarity%20Inverted%20(Active%20LOW).md) | PC3 polarity inverted to active-LOW | GPIO output polarity decision |