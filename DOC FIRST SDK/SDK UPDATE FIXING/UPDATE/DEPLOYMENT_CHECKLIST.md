# PB1 Complete Fix - Deployment & Testing Checklist

## ✅ Code Fixes Verified In Place

### Fix 1: Enable PB1 Key Events (Lines 192-194)
```c
// Verify: Line 192-194 should show:
#if !TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE
    if (__this->config->eartch_en && (ch == __this->config->eartch_ch)) {
        return;
    }
#endif
```
**Status:** ✅ APPLIED

### Fix 2: Debug Logging (Lines 209-212)
```c
// Verify: Should show:
#if TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE
    if (ch == 1) {
        printf("[LP_KEY]CH1_DETECTED: type=%d\n", event->type);
    }
#endif
```
**Status:** ✅ APPLIED

### Fix 3: Enable PB1 LONG Press Events (Lines 1474-1481)
```c
// Verify: Line 1474-1481 should show:
#if !TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE
    if (__this->config->eartch_en && (__this->config->eartch_ch == ch_num)) {
        if (__this->eartch_inear_ok) {
            ctmu_eartch_event_handle(LP_EARTCH_EVENT_IN_STATE);
        }
        break;
    }
#endif
```
**Status:** ✅ APPLIED

### Fix 4: Swap In-Ear/Out-Ear Thresholds (Lines 803-806)
```c
// Verify: Should show SWAPPED assignments:
M2P_CTMU_INEAR_VALUE_L = __this->config->eartch_soft_outear_val & 0xFF;
M2P_CTMU_INEAR_VALUE_H = __this->config->eartch_soft_outear_val >> 8;
M2P_CTMU_OUTEAR_VALUE_L = __this->config->eartch_soft_inear_val & 0xFF;
M2P_CTMU_OUTEAR_VALUE_H = __this->config->eartch_soft_inear_val >> 8;
```
**Status:** ✅ APPLIED

### Fix 5: Match PB1 Sensitivity to PB4 (Lines 67-76)
```c
// Verify: PB1 (CH1) sensitivity table now matches PB4 (CH3):
//ch1  PB1 - Now matches PB4
    {   10,    15,   152}, // level 0
    {   10,    15,   140}, // level 1
    {   10,    15,   128}, // level 2
    {   10,    15,   116}, // level 3
    {   10,    15,   104}, // level 4
    {   10,    15,    92}, // level 5
    {   10,    15,    81}, // level 6
    {   10,    15,    69}, // level 7 ← Now 69, not 57
    {   10,    15,    57}, // level 8
    {   10,    15,    45}, // level 9
```
**Status:** ✅ APPLIED

## ✅ Firmware Build Status

- **Binary:** `cpu/br28/tools/sdk.elf`
- **Size:** 5.2 MB
- **Compilation Errors:** 0
- **Compilation Warnings:** 0
- **Build Status:** ✅ SUCCESS

## ✅ Git Commits

```
d2172f9 FIX: Match PB1 sensitivity table to PB4 for consistent touch detection
6e61ed0 FIX: Swap in-ear/out-ear threshold assignments - was reversed
1e3509a ADD: Complete deliverables index
b5e276a CRITICAL FIX: Remove CH1 LONG press blocking
b5ce1de DEBUG: Add CH1 touch detection logging
```

## 📋 Pre-Deployment Verification Checklist

- [x] Code Fix 1: PB1 key event generation enabled (line 192)
- [x] Code Fix 2: Debug logging added (line 209)
- [x] Code Fix 3: LONG press events enabled (line 1474)
- [x] Code Fix 4: In-ear/out-ear thresholds swapped (line 803)
- [x] Code Fix 5: Sensitivity matched to PB4 (line 67)
- [x] Firmware compiled successfully
- [x] All changes committed to git
- [x] Zero build errors and warnings

## 🚀 Next Steps for User

### Step 1: Flash Firmware
- Deploy `cpu/br28/tools/sdk.elf` to JL7016G device
- Use your standard OTA/flash tool

### Step 2: Connect to Serial Console
- Monitor logs as device boots
- Watch for: `[LP_KEY]M2P_CTMU_CH_ENABLE = 0xa` (CH1 and CH3 enabled)

### Step 3: Test PB1 Touches
**SHORT Press:**
- Touch PB1 briefly
- Expected log: `[LP_KEY]CH1_DETECTED: type=0`
- Expected log: `soft inear` (when touching)
- Expected log: `soft outear` (when released)

**LONG Press:**
- Hold PB1 for > 1 second
- Expected log: `[LP_KEY]CH1_DETECTED: type=1`
- Expected log: `[LP_KEY]CH1: LONG click`

### Step 4: Verify Sensitivity
- PB1 should respond as easily as PB4
- Both use identical sensitivity values
- Touch detection should feel natural, not overly sensitive

### Step 5: Compare with PB4
- Touch PB4: Should trigger `[LP_KEY]CH3: RAISING`
- Touch PB1: Should trigger `[LP_KEY]CH1: RAISING`
- Behavior and responsiveness should be identical

## ✅ Success Criteria

User will know fixes are working when:

1. **PB1 generates events:** Debug output shows `[LP_KEY]CH1_DETECTED` messages
2. **In-ear detection correct:** Touching shows "soft inear", releasing shows "soft outear"
3. **Sensitivity matches:** PB1 touches as easily as PB4 - no harder to trigger
4. **LONG press works:** Holding PB1 generates LONG press events
5. **Logging shows CH1:** Boot log confirms CH1 in `M2P_CTMU_CH_ENABLE = 0xa`

---

## 📝 Technical Summary

**Root Causes Found:**
1. CH1 key events unconditionally blocked at event dispatcher entry
2. CH1 LONG press events unconditionally blocked in LONG press handler
3. In-ear/out-ear threshold registers swapped
4. PB1 sensitivity table different from PB4 (more sensitive, causing issues)

**Solutions Applied:**
1. Wrapped CH1 blocking with configuration flag check
2. Wrapped CH1 LONG press blocking with configuration flag check
3. Swapped threshold register assignments
4. Updated PB1 sensitivity table to match PB4 exactly

**Configuration:**
- `TCFG_LP_EARTCH_PRIMARY_KEY_EVENT_ENABLE = 1` (enables PB1)
- `TCFG_LP_EARTCH_SOFT_INEAR_VAL = 1500` (high threshold)
- `TCFG_LP_EARTCH_SOFT_OUTEAR_VAL = 800` (low threshold)

---

## 📞 If Issues Persist After Deployment

1. **No debug output:** Verify serial console connected properly
2. **Still reversed:** Check line 803-806 swapped values actually applied
3. **Still wrong sensitivity:** Verify line 67-76 updated to match PB4 table
4. **Still no events:** Verify lines 192 and 1474 have flag guards

---

**All code changes verified in place. Firmware ready for deployment and testing.**
