# IN-EAR DETECTION TROUBLESHOOTING GUIDE

## Issue: "It's not working" — In-Ear Detection Not Triggering

### Root Causes & Solutions

---

## 1. **Firmware Not Flashed** ⚠️ (Most Common)

**Symptom:** Configuration changed but no behavior change on board.

**Solution:**
- ✅ Rebuild: `.vscode\winmk.bat all`
- ✅ Flash/upload new firmware to the board
- ✅ Power cycle the board
- ✅ Test again

---

## 2. **PB1 and PB4 Pads Not Physically Exposed on PCB** ⚠️ (Second Most Common)

**Symptom:** Touching anything does nothing, no debug output.

**Check:**
1. **Look at your physical PCB** — are there capacitive pads/test points labeled PB1 and PB4?
   - If NO → You cannot use CTMU method on this board
   - If YES → Continue to next section

**Solution if pads missing:**
- Use **Option B: IR Sensor** (if you have IR emitter + receiver on board)
- Use **Option C: External Touch IC** (if you have external touch chip)
- OR: Disable in-ear detection entirely

---

## 3. **Sensitivity Too High or Too Low**

**Symptom:** Pad responds, but very erratic or only sometimes works.

**Diagnosis:** 
```c
// Current config (board_jl7016g_hybrid_cfg.h):
#define TCFG_LP_TOUCH_KEY1_SENSITIVITY  5      // PB1 (primary)
#define TCFG_LP_TOUCH_KEY3_SENSITIVITY  5      // PB4 (reference)
```

**Sensitivity Scale:**
- **0–2:** Very low → only hard contact triggers
- **3–5:** Moderate → typical earbuds (CURRENT SETTING)
- **6–8:** High → light touch triggers
- **9:** Very high → might trigger randomly

**Solution:**
If **no detection at all** → Increase sensitivity:
```c
#define TCFG_LP_TOUCH_KEY1_SENSITIVITY  7      // Try 7–8
#define TCFG_LP_TOUCH_KEY3_SENSITIVITY  7
```

If **random false positives** → Decrease sensitivity:
```c
#define TCFG_LP_TOUCH_KEY1_SENSITIVITY  3      // Try 3–4
#define TCFG_LP_TOUCH_KEY3_SENSITIVITY  3
```

Then rebuild, flash, and test again.

---

## 4. **Threshold Values Wrong for Your PCB**

**Symptom:** Pad detects touch, but detection algorithm never fires.

**Current thresholds:**
```c
#define TCFG_LP_EARTCH_SOFT_INEAR_VAL   3000   // Delta > 3000 = IN
#define TCFG_LP_EARTCH_SOFT_OUTEAR_VAL  2000   // Delta < 2000 = OUT
```

**Issue:** PCB pad material, distance, and size affect capacitance delta.

**Solution:** Lower the thresholds:
```c
#define TCFG_LP_EARTCH_SOFT_INEAR_VAL   1500   // Try lower threshold
#define TCFG_LP_EARTCH_SOFT_OUTEAR_VAL  800    // Hysteresis: 800-1500
```

Test in this order:
1. IN threshold: 1500 → 2000 → 3000 (increase until it works)
2. OUT threshold: 800 → 1200 → 1500 (keep gap of ~800 between IN and OUT)

---

## 5. **Reference Channel (PB4) Has No Isolation**

**Symptom:** Works sometimes, but inconsistent.

**Cause:** PB4 is also touching the ear or in contact with sweat/moisture.

**Solution:** Physically ensure PB4:
- Is **NOT in the ear** (positioned outside, on earphone casing)
- Is **NOT on the wearing surface** (should be isolated)
- Stays **relatively constant** (only provides reference baseline)

**Or use differential mode calibration:**
```c
// Increase PB4 (reference) sensitivity to better reject noise
#define TCFG_LP_TOUCH_KEY3_SENSITIVITY  8      // Reference higher sensitivity
#define TCFG_LP_TOUCH_KEY1_SENSITIVITY  5      // Primary normal sensitivity
```

---

## 6. **CTMU Hardware Not Initialized**

**Symptom:** LP touch other than eartch works, but in-ear detection silent.

**Verify config enables the feature:**
```c
// board_jl7016g_hybrid_cfg.h
#define TCFG_LP_TOUCH_KEY_ENABLE        ENABLE_THIS_MOUDLE    // ✅ MUST be enabled
#define TCFG_LP_TOUCH_KEY1_EN           1                     // ✅ PB1 enabled
#define TCFG_LP_TOUCH_KEY3_EN           1                     // ✅ PB4 enabled
#define TCFG_LP_EARTCH_KEY_ENABLE       1                     // ✅ Eartch enabled
#define TCFG_EARTCH_EVENT_HANDLE_ENABLE ENABLE_THIS_MOUDLE    // ✅ App handler enabled
```

If ANY of these are disabled/wrong, rebuild and flash.

---

## 7. **App Event Handler Not Receiving Events**

**Symptom:** Debug shows CTMU firing, but no music pause/resume.

**Check if app is handling the event:**

Enable debug output:
```c
// apps/earphone/eartch_event_deal.c line 21
#define LOG_DEBUG_ENABLE                        // Add this line
```

Then rebuild, flash, and check debug output when touching PB1.

You should see logs like:
```
[EARTCH_EVENT_DEAL] update local_state: 1      // IN detected
[EARTCH_EVENT_DEAL] SEND PLAY                  // Music resumed
```

If no logs → App event handler is disabled or not running.

---

## 8. **Bluetooth Not Connected**

**Symptom:** In-ear detection works but music doesn't pause/resume.

**Cause:** No A2DP (music) link established.

**Solution:**
1. Ensure BT is connected to phone
2. Ensure music app is ready
3. Test: pause music → remove earpiece → should stay paused
4. Test: insert earpiece → should resume if eartch detected

---

## Quick Test Procedure

1. **Enable CTMU and in-ear detection** ✅ (already done)
2. **Rebuild and flash firmware** ✅
3. **Open debug console** and power on board
4. **Slowly touch PB1 pad** with finger for ~2 seconds
5. **Check debug output** for:
   - Capacitance values changing?
   - State change to IN/OUT?
   - App log messages?

**If YES to any** → In-ear detection is working; check app logic next
**If NO to all** → Check PB1/PB4 pad hardware; verify sensitivity/thresholds

---

## Recommended Tuning Steps

### Step 1: Verify Pads Exist
- Visual inspection of PCB
- Multimeter continuity check to CTMU pins

### Step 2: Lower Thresholds (Most Likely Fix)
```c
#define TCFG_LP_EARTCH_SOFT_INEAR_VAL   1500   // Down from 3000
#define TCFG_LP_EARTCH_SOFT_OUTEAR_VAL  800    // Down from 2000
```

### Step 3: Increase Sensitivity
```c
#define TCFG_LP_TOUCH_KEY1_SENSITIVITY  7      // Up from 5
#define TCFG_LP_TOUCH_KEY3_SENSITIVITY  7
```

### Step 4: Enable Debug Output
Add `#define LOG_DEBUG_ENABLE` to `lp_touch_key.c` to see raw capacitance values.

### Step 5: Verify App Event Handling
Ensure `TCFG_EARTCH_EVENT_HANDLE_ENABLE = ENABLE_THIS_MOUDLE`

---

## Configuration Reference

**File:** `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h`

**Key Macros:**
| Macro | Current | Purpose |
|-------|---------|---------|
| `TCFG_LP_TOUCH_KEY_ENABLE` | `ENABLE_THIS_MOUDLE` | Master CTMU enable |
| `TCFG_LP_TOUCH_KEY1_EN` | `1` | Enable PB1 (primary) |
| `TCFG_LP_TOUCH_KEY3_EN` | `1` | Enable PB4 (reference) |
| `TCFG_LP_EARTCH_KEY_ENABLE` | `1` | Enable in-ear detection |
| `TCFG_LP_EARTCH_KEY_CH` | `1` | Primary ch = ch1 (PB1) |
| `TCFG_LP_EARTCH_KEY_REF_CH` | `3` | Reference ch = ch3 (PB4) |
| `TCFG_LP_EARTCH_SOFT_INEAR_VAL` | `3000` | **← Try lowering to 1500** |
| `TCFG_LP_EARTCH_SOFT_OUTEAR_VAL` | `2000` | **← Try lowering to 800** |
| `TCFG_LP_TOUCH_KEY1_SENSITIVITY` | `5` | **← Try raising to 7–8** |
| `TCFG_LP_TOUCH_KEY3_SENSITIVITY` | `5` | **← Try raising to 7–8** |

---

## Most Likely Fix for "Not Working"

Based on typical PCB variations:

**99% of cases:** Thresholds are too high for your specific PCB pads.

**Fix:**
1. Lower `TCFG_LP_EARTCH_SOFT_INEAR_VAL` from 3000 → **1500**
2. Lower `TCFG_LP_EARTCH_SOFT_OUTEAR_VAL` from 2000 → **800**
3. Rebuild and flash
4. Test

If still not working after 2 mins of touch:
- Increase sensitivity: 5 → **7**
- Test again

---

## Still Not Working After These Steps?

1. **Verify PB1 and PB4 pads physically exist** on your PCB (most likely issue)
2. **Check board schematic** — confirm CTMU is wired correctly
3. **Use multimeter** — verify GPIO continuity to CTMU input pins
4. **Consider IR sensor or external touch IC** as alternative
5. **Disable in-ear detection** if not needed

---

## Related FIX Records

| Fix | Title | Relevance |
|-----|-------|-----------|
| [FIX-007](../../FIXING/FIX-007%20—%20PB4%20gestures%20dropped%20on%20eartch%20reference%20channel.md) | PB4 gestures dropped on eartch reference | Gesture detection debugging |
| [FIX-008](../../FIXING/FIX-008%20—%20CH3%20long%20hold%20suppressed%20by%20long-by-res%20gate.md) | CH3 long/hold suppressed | Long-press detection |
| [FIX-009](../../FIXING/FIX-009%20—%20PB4%20touch%20range%20rejected%20by%20low%20algorithm%20max.md) | PB4 touch range rejected | Touch threshold troubleshooting |
| [FIX-015](../../FIXING/FIX-015%20—%20PB1_COMPLETE_SOLUTION.md) | PB1 complete solution | PB1/CH1 channel bring-up |

