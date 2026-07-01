# IN-EAR DETECTION — CTMU Capacitive Sensing, GPIO Mapping, State Machine

## Overview

In-ear detection (入耳检测 / 佩戴检测 / eartch) is a **wear detection system** that continuously monitors whether the earbuds are inserted in the user's ears. When the system detects that an earbud enters or exits the ear, it automatically triggers pre-programmed actions: music pauses when removed, resumes when inserted; during calls, audio routes to the phone speaker when earbuds are removed, and back to the earphone when inserted.

**Current Status on JL7016G Hybrid Board:** ✅ **ENABLED** — CTMU capacitive sensing on `PB1` (primary, CTMU ch1) and `PB4` (reference, CTMU ch3).

---

## How It Works — The Capacitive Sensing Method

### The CTMU Sensor

The BR28 chip has a built-in **CTMU** (Capacitive Touch Module Unit) that can sense changes in capacitance. On the JL7016G Hybrid board, two channels are used for in-ear detection:

- **Primary Channel (PB1, CTMU ch1)** — The pad that physically touches or is near your ear when worn
- **Reference Channel (PB4, CTMU ch3)** — A reference pad that is NOT in contact with your ear; provides a baseline

### The Algorithm

1. **CTMU continuously reads** the capacitance on both channels
2. **Calculates delta** (difference) = primary capacitance − reference capacitance
3. **Compares delta against thresholds:**
   - If delta **> 1500** → earpiece **DETECTED IN EAR** → fires `EARTCH_STATE_IN` event
   - If delta **< 800** → earpiece **DETECTED OUT OF EAR** → fires `EARTCH_STATE_OUT` event
   - Between 800–1500 → **hysteresis zone** (no state change; prevents jitter)

### The Z-Score Algorithm

`cpu/br28/lp_touch_key_alog.c` implements a sophisticated signal processing pipeline:

1. **Capacitance Sampling** — CTMU samples raw delta values ~10 ms per reading
2. **IIR Low-Pass Filter** — Sigma IIR filter smooths noise (configurable filter coefficient)
3. **Z-Score Calculation** — Computes `(sample - mean) / std_dev` to detect outliers
4. **Valley/Peak Detection** — Identifies the signal's trend direction
5. **Gradient Analysis** — Detects edges (rapid changes in capacitance)
6. **Decision** — When gradient crosses threshold + z-score is high enough → state change

**Why this approach?**
- Robust against noise (sweat, thermal drift, humidity)
- Adapts to pad aging and material changes
- Distinguishes between "in ear" and "ear nearby"

---

## GPIO Pin Mapping

| Signal                | GPIO  | CTMU Channel | Hardware       | Purpose                     |
| --------------------- | ----- | ------------ | -------------- | --------------------------- |
| **Primary Channel**   | `PB1` | ch1          | Capacitive pad | Senses ear insertion        |
| **Reference Channel** | `PB4` | ch3          | Capacitive pad | Baseline/drift compensation |

**How they're wired:**
- Both are capacitive pads on the PCB
- `PB1` is positioned to detect ear contact
- `PB4` is isolated (or positioned away from ear contact) to provide a reference signal

**Electrical Connection:**
- Both pads connect to CTMU input pins via **charge pump** circuit
- Capacitance change is detected by **charging/discharging cycles**
- Delta is calculated in hardware and reported to firmware

---

## Configuration Macros

All settings are in `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h`:

### Enable/Disable the Feature

```c
#define TCFG_LP_TOUCH_KEY_ENABLE    ENABLE_THIS_MOUDLE    // line ~165: Master on/off for all LP touch features
#define TCFG_LP_TOUCH_KEY1_EN       1                     // line ~170: Enable PB1 primary channel
#define TCFG_LP_TOUCH_KEY3_EN       1                     // line ~172: Enable PB4 reference channel
#define TCFG_LP_EARTCH_KEY_ENABLE   1                     // line ~183: Enable in-ear detection specifically
```

### Threshold Configuration

```c
#define TCFG_LP_EARTCH_KEY_CH           1      // Primary channel for eartch: CTMU ch1 = PB1
#define TCFG_LP_EARTCH_KEY_REF_CH       3      // Reference channel for eartch: CTMU ch3 = PB4
#define TCFG_LP_EARTCH_SOFT_INEAR_VAL   1500   // IN-EAR threshold: delta > 1500 → IN state
#define TCFG_LP_EARTCH_SOFT_OUTEAR_VAL  800    // OUT-OF-EAR threshold: delta < 800 → OUT state
```

### Sensitivity Fine-Tuning

```c
#define TCFG_LP_TOUCH_KEY1_SENSITIVITY  7      // Primary channel (PB1) sensitivity (0–9): higher = more sensitive
#define TCFG_LP_TOUCH_KEY3_SENSITIVITY  7      // Reference channel (PB4) sensitivity (0–9): higher = more sensitive
```

**Sensitivity Tuning Guidelines:**
- **0–3:** Thick pads, low capacitance change, coarse material
- **4–6:** Typical earbuds, PCB traces through plastic
- **7–9:** Thin pads, high capacitance change, fine materials
- **Recommendation:** Start at 5; if no in-ear detection, increase to 6–7; if too many false positives, decrease to 4

---

## State Machine & Event Flow

```
┌──────────────────────────────────────┐
│         EARTCH_STATE_OUT             │
│   (Earpiece removed from ear)        │
│                                      │
│  • Music: PAUSED                     │
│  • Call: SCO routed to PHONE         │
│  • TWS: Can trigger master swap      │
└──────────────────────────────────────┘
            ▲                │
            │                │ delta > 1500 for 500ms+
            │                ▼
            │    ┌─────────────────────┐
            │    │ Hysteresis zone     │
            │    │ (800 < delta < 1500) │
            │    │ → No state change   │
            │    └─────────────────────┘
            │                │
            │                ▼
delta < 800 └──────────────────────────────────────┐
            for 500ms+       |                       │
                             ▼                       ▼
            ┌──────────────────────────────────────┐
            │        EARTCH_STATE_IN               │
            │   (Earpiece inserted in ear)         │
            │                                      │
            │  • Music: RESUMED (if was playing)  │
            │  • Call: SCO routed to EARPHONE      │
            │  • TWS: Can trigger master swap      │
            │  • Tone: Brief beep plays            │
            └──────────────────────────────────────┘
```

**Transition Timing:**
- **Debounce filter:** 500 ms (5 consecutive reads in same state)
- **Purpose:** Prevents false triggers from quick motion (scratching ear, adjusting fit)

---

## What Happens on IN-EAR Detection

When firmware detects `EARTCH_STATE_IN` (earpiece inserted and capacitance delta crosses 1500 threshold):

### 1. **Audio Callback**
   - Plays a short **tone** (`TONE_NORMAL`) to confirm detection
   - Provides tactile feedback that the system detected insertion

### 2. **Music Control** (if not on a call)
   - If A2DP (music streaming) is **connected:**
     - Sends `USER_CTRL_AVCTP_OPID_PLAY` command → **music resumes**
   - Starts a state monitor timer to verify music actually started
   - If music doesn't start after 1 second, retries the PLAY command

### 3. **Call Control** (if on an active call)
   - If SCO (call audio link) is **disconnected:**
     - Sends `USER_CTRL_CONN_SCO` command → **SCO reconnects**
     - Call audio routes from phone speaker → earphone microphone/speaker
   - Enables call-to-earpiece routing for VoIP/cellular calls

### 4. **TWS Master/Slave Sync** (if paired earbuds)
   - If this earbud is master and sibling is slave:
     - Broadcasts `EARTCH_STATE_IN` event to sibling via `TWS_FUNC_ID_EARTCH_SYNC`
   - If master is OUT but this slave is IN:
     - Firmware can **swap master role** (if `TCFG_EARTCH_AUTO_CHANGE_MASTER = 1`)
     - New master handles call routing; old master goes idle

### 5. **Music Control Timeout Cancellation**
   - If there's an active 15-second timeout waiting for re-insertion, **it's canceled**
   - Ensures music doesn't pause while wearing the earphone

---

## What Happens on OUT-OF-EAR Detection

When firmware detects `EARTCH_STATE_OUT` (earpiece removed; delta drops below 800):

### 1. **Music Control** (if not on a call)
   - If A2DP is **connected and playing:**
     - Sends `USER_CTRL_AVCTP_OPID_PAUSE` command → **music pauses immediately**
   - If A2DP is disconnected (optional behavior):
     - Can send `USER_CTRL_DISCONN_A2DP` to route music to phone speaker
     - Controlled by `TCFG_EARTCH_MUSIC_CTL_A2DP_CONNECT` (currently disabled)

### 2. **Music Control Timeout** (optional 15-second re-wear grace period)
   - If `TCFG_EARTCH_MUSIC_CTL_TIMEOUT_ENABLE = 1`:
     - Sets a **15-second timer**
     - If earpiece is re-worn within 15 seconds → timer canceled, music resumes
     - If 15 seconds elapse → music **remains paused** (user is not wearing it)
   - **Currently disabled** on this board (`TCFG_EARTCH_MUSIC_CTL_TIMEOUT_ENABLE = 0`)

### 3. **Call Control** (if on an active call)
   - If both earpieces are **OUT** (TWS) or single earbud:
     - Sends `USER_CTRL_DISCONN_SCO` command → **SCO disconnects**
     - Call audio routes from earphone → phone speaker/microphone
     - User hears call via phone speaker; phone mic is active

### 4. **TWS Master/Slave Sync** (if paired earbuds)
   - If this earbud is master and sibling is slave:
     - Broadcasts `EARTCH_STATE_OUT` event to sibling
   - If master is OUT but sibling is IN (during a call):
     - Firmware can **swap master role** (handles audio routing)
     - New master continues the call; old master powers down to low-power listening

### 5. **No Tone Playback**
   - Unlike IN-EAR detection, removal does **NOT** play a confirmation tone
   - Rationale: Avoids ear annoyance when quickly removing earphones

---

## Current Board Configuration Summary

**JL7016G Hybrid — In-Ear Detection Status:**

| Setting | Value | Status |
|---------|-------|--------|
| CTMU Master Enable | `ENABLE_THIS_MOUDLE` | ✅ ENABLED |
| PB1 (Primary Ch., ch1) | `1` | ✅ ENABLED |
| PB4 (Reference Ch., ch3) | `1` | ✅ ENABLED |
| In-Ear Eartch Enable | `1` | ✅ ENABLED |
| IN-EAR Threshold | `1500` | ✅ CONFIGURED |
| OUT-OF-EAR Threshold | `800` | ✅ CONFIGURED |
| Sensitivity (both ch.) | `7` | ✅ TUNED |
| App Event Handler | Auto-enabled | ✅ ACTIVE |
| TWS Auto Master Swap | `ENABLE_THIS_MOUDLE` | ✅ ENABLED |
| Call SCO Control | `1` (enabled) | ✅ ACTIVE |
| Music Control | `1` (enabled) | ✅ ACTIVE |

**Expected Behavior:**
- ✅ Earpiece inserted (PB1 pad touched) → Music resumes, call audio routes to earphone, tone plays
- ✅ Earpiece removed (PB1 pad untouched) → Music pauses, call audio routes to phone speaker
- ✅ TWS sibling state synchronized automatically
- ✅ PB4 reference channel continuously compensates for environmental drift

---

## Driver Code Flow

### Firmware Entry Points

1. **CTMU Interrupt Handler** (`cpu/br28/lp_touch_key.c` L388)
   ```c
   ctmu_eartch_event_handle()  // Called on every CTMU sample
    ↓
   eartch_state_update(EARTCH_STATE_IN or EARTCH_STATE_OUT)  // Update state
    ↓
   ```

2. **Event Routing** (`apps/earphone/eartch_event_deal.c` L107)
   ```c
   eartch_event_deal_enable()  // Initialize on boot
    ↓
   eartch_post_event(state)  // Send SYS_DEVICE_EVENT
    ↓
   eartch_handle()  // Process IN or OUT state
    ↓
   eartch_in_bt_control_handle()  or  eartch_out_bt_control_handle()
    ↓
   eartch_send_bt_ctrl_cmd(USER_CTRL_AVCTP_OPID_PLAY/PAUSE/CONN_SCO/DISCONN_SCO)
   ```

3. **TWS Sync** (`apps/earphone/eartch_event_deal.c` L223)
   ```c
   eartch_sync_tws_state(state)  // Broadcast to sibling earbud
    ↓
   tws_api_send_data_to_sibling(..., TWS_FUNC_ID_EARTCH_SYNC)
   ```

### Key Functions

| Function | Location | Purpose |
|----------|----------|---------|
| `ctmu_eartch_event_handle()` | `cpu/br28/lp_touch_key.c` L388 | CTMU interrupt → state update |
| `eartch_state_update()` | `apps/earphone/eartch_event_deal.c` L680 | Register state change locally |
| `eartch_event_handle()` | `apps/earphone/eartch_event_deal.c` L750 | Process event (debounce + callback) |
| `eartch_handle()` | `apps/earphone/eartch_event_deal.c` L705 | Execute IN/OUT behaviors |
| `eartch_in_bt_control_handle()` | `apps/earphone/eartch_event_deal.c` L395 | Music/call actions on IN |
| `eartch_out_bt_control_handle()` | `apps/earphone/eartch_event_deal.c` L432 | Music/call actions on OUT |
| `eartch_sync_tws_state()` | `apps/earphone/eartch_event_deal.c` L223 | Sync to sibling earbud |

---

## Power Management & Sleep

**In Low Power / Sleep Mode:**
- The CTMU sensor can remain **active as a wake-up source** (enabled via `power_config_lpctmu_en()`)
- User taps the earbud's touch pad → CTMU detects capacitance change → wakes CPU
- In-ear detection **does not** affect sleep; the algorithm continues running

**Power Impact:**
- CTMU running continuously consumes ~2–5 µA per channel (negligible vs. Bluetooth RF)
- Not a significant battery drain for typical earphones

---

## Advanced Tuning & Troubleshooting

## UART Log And Debug Verification

UART logging is enabled for this board and now includes detailed in-ear debug output.

- UART TX pin: `PB5`
- Baudrate: `115200`
- UART module: enabled via `TCFG_UART0_ENABLE`

Enabled debug points:

- `cpu/br28/lp_touch_key.c`: `LOG_DEBUG_ENABLE`
- `apps/earphone/eartch_event_deal.c`: `LOG_DEBUG_ENABLE`
- `apps/earphone/log_config/app_config.c`: `log_tag_const_d_EARTCH_EVENT_DEAL = TRUE`

Expected UART tags during test:

- `[LP_KEY]` for touch/raw state transitions
- `[EARTCH_EVENT_DEAL]` for ear in/out behavior and control commands

Quick validation flow:

1. Rebuild and flash firmware.
2. Connect serial tool to `115200`.
3. Set terminal format to `8 data bits, no parity, 1 stop bit (8N1), no flow control`.
4. Touch PB1 (wear simulation), keep PB4 as reference pad.
5. Confirm logs show in-ear state update and play/SCO control actions.
6. Release PB1 and verify out-ear logs + pause/SCO disconnect actions.

### Latest Behavior Fix (CH3 Long-Click Interference)

Observed issue from logs:
- `CH3: LONG click` and `CH3: FALLING` kept firing while in-ear detection was active.
- This made ear-detect channels also behave like normal touch keys, causing side effects (volume/audio change).

Applied fix in `cpu/br28/lp_touch_key.c`:
- Ear-detect channels (`eartch_ch` and `eartch_ref_ch`) are now blocked from normal key event delivery.
- Added single-touch fallback behavior on primary ear channel:
  - press/long-press on primary channel => `IN-EAR`
  - release on primary channel => `OUT-EAR`

Result:
- PB1 can be used as "hold = in-ear" behavior.
- PB4 remains reference for CTMU differential stability.
- Normal key side effects from CH3 are suppressed.

### False Positives (Constant "IN" Detection)

**Symptoms:** Music keeps playing even when earpiece is removed.

**Causes:**
- Pad material is conductive (sweat, dirt)
- `TCFG_LP_EARTCH_SOFT_INEAR_VAL` is too low
- `TCFG_LP_TOUCH_KEY1_SENSITIVITY` is too high

**Solutions:**
1. Increase `TCFG_LP_EARTCH_SOFT_INEAR_VAL` from 3000 → 4000–5000
2. Decrease `TCFG_LP_TOUCH_KEY1_SENSITIVITY` from 7 → 5–6
3. Verify PCB pad layout — reference channel (`PB4`) should be isolated from ear contact

### False Negatives (No Detection When Inserted)

**Symptoms:** Music doesn't resume when wearing; earpiece detection never triggers.

**Causes:**
- Pad material is poorly conductive or isolated
- `TCFG_LP_EARTCH_SOFT_INEAR_VAL` is too high
- `TCFG_LP_TOUCH_KEY1_SENSITIVITY` is too low
- Reference channel (`PB4`) is not isolated properly

**Solutions:**
1. Decrease `TCFG_LP_EARTCH_SOFT_INEAR_VAL` from 3000 → 2000–2500
2. Increase `TCFG_LP_TOUCH_KEY1_SENSITIVITY` from 7 → 8–9
3. Verify PCB connectivity; check for solder shorts between pads
4. Verify `TCFG_LP_TOUCH_KEY1_EN = 1`, `TCFG_LP_TOUCH_KEY3_EN = 1`, and `TCFG_LP_EARTCH_KEY_ENABLE = 1`

### Jitter / Frequent Toggling

**Symptoms:** Music starts/stops repeatedly; state changes too often.

**Causes:**
- Thresholds are in the hysteresis zone (800–1500)
- User is moving the earpiece around (wearing, adjusting fit)
- Environmental noise (humidity, temperature drift)

**Solutions:**
1. Verify hysteresis gap: `INEAR_VAL (1500) - OUTEAR_VAL (800) = 700` is typical
2. If gap is too small (< 500), increase `OUTEAR_VAL` or decrease `INEAR_VAL`
3. Verify `TCFG_LP_TOUCH_KEY1_SENSITIVITY` and `TCFG_LP_TOUCH_KEY3_SENSITIVITY` are balanced (both 7)
4. Check board temperature; thermal drift can affect capacitance slightly

---

## Related Files

| File | Role |
|------|------|
| [board_jl7016g_hybrid_cfg.h](../../apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h) | Board config macros |
| [board_jl7016g_hybrid.c](../../apps/earphone/board/br28/board_jl7016g_hybrid.c) | Hardware init struct |
| [eartch_event_deal.c](../../apps/earphone/eartch_event_deal.c) | App event handler |
| [lp_touch_key.c](../../cpu/br28/lp_touch_key.c) | CTMU driver |
| [lp_touch_key_alog.c](../../cpu/br28/lp_touch_key_alog.c) | Capacitive algorithm |
| [in_ear_detect.c](../../apps/common/device/in_ear_detect/in_ear_detect.c) | IR/touch driver (external) |
| [in_ear_manage.c](../../apps/common/device/in_ear_detect/in_ear_manage.c) | State machine |
| [key_event_deal.h](../../apps/earphone/include/key_event_deal.h) | Event enum definitions |

---

## Summary

| Aspect | Detail |
|--------|--------|
| **Mechanism** | BR28 CTMU capacitive sensing (built-in, no extra IC) |
| **GPIO Pins** | PB1 (reference), PB2 (primary) |
| **Detection Method** | Differential capacitance comparison with thresholds |
| **Algorithm** | Z-score + valley/peak detection + IIR filtering |
| **IN-EAR Behavior** | Resume music, route call to earphone, play tone, TWS sync |
| **OUT-OF-EAR Behavior** | Pause music, route call to phone, TWS sync |
| **Hysteresis** | 2000–3000 (prevents jitter) |
| **Debounce** | 500 ms (5 consecutive valid reads) |
| **Power Impact** | ~2–5 µA per channel (negligible) |
| **Status on JL7016G Hybrid** | ✅ ENABLED |

---

## Related FIX Records

| Fix | Title | Relevance |
|-----|-------|-----------|
| [FIX-007](../../FIXING/FIX-007%20—%20PB4%20gestures%20dropped%20on%20eartch%20reference%20channel.md) | PB4 gestures dropped on eartch reference | CTMU channel event routing |
| [FIX-008](../../FIXING/FIX-008%20—%20CH3%20long%20hold%20suppressed%20by%20long-by-res%20gate.md) | CH3 long/hold suppressed | CTMU long-press gating |
| [FIX-009](../../FIXING/FIX-009%20—%20PB4%20touch%20range%20rejected%20by%20low%20algorithm%20max.md) | PB4 touch range rejected | CTMU threshold/algorithm |
| [FIX-010](../../FIXING/FIX-010%20—%20in-ear%20remap%20hook%20active%20while%20ear%20detect%20disabled.md) | In-ear remap hook active while disabled | In-ear state machine / event intercept |
| [FIX-015](../../FIXING/FIX-015%20—%20PB1_COMPLETE_SOLUTION.md) | PB1 complete solution | CH1 bring-up, GPIO-only role |

