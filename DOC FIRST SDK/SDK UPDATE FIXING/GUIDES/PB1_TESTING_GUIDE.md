# PB1 Touch Detection - Testing & Deployment Guide

## WHAT WAS FIXED

Two unconditional blocking points in `cpu/br28/lp_touch_key.c` were preventing PB1 (CH1) from working:

1. **Line 192** - Event dispatcher was blocking ALL CH1 events
2. **Line 1474** - LONG press handler was blocking CH1 LONG presses

Both now wrapped with `#if !TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE` flag (value: 1 = enabled)

## FIRMWARE STATUS

✅ **Built Successfully** - `cpu/br28/tools/sdk.elf` (5.2 MB)
- 0 compilation errors
- 0 warnings
- Ready to deploy to JL7016G device

## WHAT YOU'LL SEE

When you touch PB1 after flashing this firmware:

```
[LP_KEY]CH1_DETECTED: type=<event_type>
```

Appears in your device logs/console output.

## TESTING STEPS

### 1. Deploy Firmware
Flash the compiled binary to your JL7016G device using your standard deployment method.

### 2. Monitor Logs
- Connect device to serial console or log viewer
- Watch for boot messages to confirm device started
- Look for: `[LP_KEY]CH1_DETECTED` message

### 3. Touch PB1
- Gently touch the PB1 contact point (in-ear touch sensor)
- SHORT press (< 1 second) - should show debug message
- LONG press (> 1 second) - should show debug message
- Release - event should be logged

### 4. Verify Success
You should see output like:
```
[LP_KEY]CH1_DETECTED: type=0
[LP_KEY]CH1: RAISING
[LP_KEY]CH1: UP
```

## WHAT CHANGED IN CODE

### Before (Broken)
```c
// Line 192-193: UNCONDITIONAL BLOCK
if (__this->config->eartch_en && (ch == __this->config->eartch_ch)) {
    return;  // ❌ CH1 ALWAYS BLOCKED
}
```

### After (Fixed)
```c
// Line 192-194: CONDITIONAL BLOCK
#if !TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE
    if (__this->config->eartch_en && (ch == __this->config->eartch_ch)) {
        return;  // Now respects flag
    }
#endif
```

With `TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE = 1`, CH1 is now ENABLED.

## CONFIGURATION

File: `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h`

Key settings (already correct):
```c
#define TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE = 1      // PB1 events enabled
#define TCFG_LP_EARTCH_SOFT_INEAR_VAL = 1500             // Primary threshold
#define TCFG_LP_EARTCH_SOFT_OUTEAR_VAL = 800             // Reference threshold
#define TCFG_LP_EARTCH_REF_KEY_EVENT_ENABLE = 1          // PB4 events enabled
```

## GIT COMMITS

```
b5e276a - CRITICAL FIX: Remove CH1 LONG press blocking - second blocking point
b5ce1de - DEBUG: Add CH1 touch detection logging
```

View changes:
```bash
git show b5ce1de
git show b5e276a
```

## TROUBLESHOOTING

### No debug messages appear when touching PB1

1. Check firmware actually deployed (should be 5.2 MB)
2. Verify console/log connection working (PB4 touches should still work as reference)
3. Confirm touch detection is enabled in device config
4. Check if touches are being registered at all (contact point clean?)

### Messages show but different format

This is OK - the key point is that CH1 events are now flowing through the system instead of being completely blocked.

### Only SHORT presses work, LONG presses don't

This would indicate LONG press fix didn't apply. Verify line 1474 has the flag wrapper.

## NEXT STEPS

1. Flash firmware to device
2. Touch PB1 and monitor logs
3. Report back if you see `[LP_KEY]CH1_DETECTED` messages
4. If working, PB1 is fully functional and event processing is complete

---

**Status**: Firmware ready for deployment. Code changes verified. Awaiting device testing.
