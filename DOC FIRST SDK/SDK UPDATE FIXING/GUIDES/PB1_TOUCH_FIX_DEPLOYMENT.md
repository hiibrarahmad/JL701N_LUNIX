# PB1 Touch Control LED Feedback - Deployment Guide

## Issue Fixed
PB1 (channel 1, primary in-ear sensor) was completely blocked from generating touch events, preventing LED feedback functionality despite being used for in-ear detection algorithm.

## Root Cause Analysis
Two core functions in `cpu/br28/lp_touch_key.c` were **unconditionally excluding CH1 from CTMU processing**:

1. **`lp_touch_key_ctmu_res_scan()`** (line ~580)
   - Scans resistance values from all active channels every cycle
   - Was skipping CH1 entirely when in-ear detection enabled

2. **`lp_touch_key_alog_ready_flag_check_and_set()`** (line ~660)
   - Initializes analog configuration at startup
   - Was skipping CH1 initialization

This meant CH1:
- ❌ Never had resistance values scanned
- ❌ Never had analog configuration initialized
- ❌ Could not generate RAISING/FALLING events
- ❌ Remained completely silent in boot logs

## Solution Implemented

### Code Changes
**File:** `cpu/br28/lp_touch_key.c`

**Change 1:** Removed CH1 exclusion from `lp_touch_key_ctmu_res_scan()`
```c
// BEFORE: 
if (__this->config->eartch_en && (__this->config->eartch_ch == ch)) {
    // Skip CH1
} else {
    u16 ctmu_res0;
    // Process channel
}

// AFTER:
u16 ctmu_res0;
// Process all channels including CH1
```

**Change 2:** Removed CH1 exclusion from `lp_touch_key_alog_ready_flag_check_and_set()`
```c
// BEFORE:
if (__this->config->eartch_en && (__this->config->eartch_ch == ch)) {
    // Skip CH1
} else {
    alog_cfg[ch].ready_flag = 0;
    // Initialize analog config
}

// AFTER:
alog_cfg[ch].ready_flag = 0;
// Initialize all channels including CH1
```

### Configuration Already Set
**File:** `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h`

```c
#define TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE   1
#define TCFG_LP_EARTCH_REF_KEY_EVENT_ENABLE       1
#define TCFG_LP_TOUCH_PB1_LED_FEEDBACK_ENABLE     1
```

## Build Results
```
✅ Status: SUCCESS
✅ Errors: 0
✅ Warnings: 0
✅ Binary: ota.bin
✅ Size: 203,904 bytes
✅ Date: 4/6/2026 1:36:01 PM
✅ Preprocessor: 59 #if / 59 #endif (balanced)
```

## Expected Behavior After Deployment

### In Boot Log
When touching PB1 (in-ear contact):
```
[LP_KEY]CH1: RAISING
[LP_KEY]CH1: FALLING
[LP_KEY]notify key1 short event
[KEY_EVENT_DEAL]key_event:xx x x
```

### On Device
1. **Touch PB1** (press/tap) → **PC3 LED turns ON** (1V active HIGH)
2. **Release PB1** (after touch) → **PC3 LED turns OFF**
3. **In-ear detection** continues working normally with CH1+CH3 soft thresholds

### LED Timing
- **CLICK/LONG/DOUBLE_CLICK events** → LED ON
- **KEY_EVENT_UP (release)** → LED OFF

## Deployment Steps

1. **Backup current firmware** if not already done
2. **Upload new OTA binary** from `cpu/br28/tools/download/earphone/ota.bin`
3. **Flash device** using your standard upgrade method (USB/Bluetooth/UART)
4. **Collect boot logs** after restart
5. **Test by touching PB1** and observing:
   - CH1 RAISING/FALLING events in logs
   - PC3 LED physical feedback on device
   - In-ear detection algorithm still running ("soft inear"/"soft outear" messages)

## Verification Checklist

After deployment, verify:
- [ ] Boot log shows `CH1: RAISING` events when touching PB1
- [ ] Boot log shows `CH1: FALLING` events when releasing PB1
- [ ] Boot log shows `notify key1` messages
- [ ] In-ear detection messages still appear (`soft inear`, `soft outear`)
- [ ] PC3 LED illuminates when touching PB1
- [ ] PC3 LED extinguishes when releasing PB1
- [ ] Device functions normally (no performance regression)

## Technical Details

### Touch Processing Pipeline
```
Hardware Interrupt (CH1 event)
  ↓
__ctmu_notify_key_event() - Event dispatcher (identifies channel)
  ↓
lp_touch_ch_event_handle() - LED handler (turns ON/OFF based on event type)
  ↓
lp_touch_key_event_remap() - Event mapper (returns 1 to allow propagation)
  ↓
sys_event_notify() - System event notification
  ↓
key_event_deal.c - Application-level key handling
```

### Channel Configuration
| Channel | Pin | Function | Status |
|---------|-----|----------|--------|
| CH1 | PB1 | In-ear PRIMARY | ✅ ENABLED (was blocked) |
| CH3 | PB4 | In-ear REFERENCE | ✅ ENABLED (working) |
| PC3 | PC3 | LED output | ✅ CONFIGURED |

### GPIO/LED Control
```c
Port: PORTC_03
Mode: Output (gpio_direction_output)
Active Level: HIGH (1V)
Control Function: gpio_write(u32 gpio, u32 value)
Initialization: key_event_deal_pb1_led_init() on first touch
```

## Files Modified
- ✅ `cpu/br28/lp_touch_key.c` - Removed CH1 processing exclusion (2 functions)
- ✅ `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h` - Configuration (already set)
- ✅ `apps/earphone/key_event_deal.c` - LED handler (already implemented)

## Git Commit
```
Commit: 472617a
Message: FIX: Remove CH1 exclusion from CTMU processing to enable PB1 touch events
```

## Rollback Instructions
If issues occur:
```bash
git revert 472617a
make clean
make all
```

## Support
For issues with PB1 not triggering events after deployment:
1. Check boot logs for CH1 RAISING/FALLING events
2. Verify `TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE = 1` in configuration
3. Check GPIO PC3 is not already assigned to other functionality
4. Verify in-ear detection algorithm is still running (soft inear/outear messages)
