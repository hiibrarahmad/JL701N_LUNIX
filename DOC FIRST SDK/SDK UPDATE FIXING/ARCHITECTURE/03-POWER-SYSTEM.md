---
tags: [architecture, power, battery, charging, sleep]
date: 2026-05-01
---

# ⚡ Power Management Architecture

**Purpose:** Understand power states, battery management, and optimization.

---

## Power States

```
Active State (Playback/Streaming)
        ↑↓  [Events: Audio → Low Power threshold]
Low Power State (Idle with BT)
        ↑↓  [Events: Touch → Active / Timeout → Sleep]
Sleep State (Deep Sleep)
        ↑↓  [Events: Wake signal → Active]
```

---

## Power Consumption

| State | Current | Duration |
|-------|---------|----------|
| **Active (Streaming)** | ~50 mA | While playing |
| **Low Power (Idle)** | ~10 mA | Waiting for input |
| **Sleep (Deep Sleep)** | ~5 μA | Case closed |

**Result:** 8-hour battery life (typical use)

---

## Hardware Components

### Power Supply
- **Battery:** Lithium-Polymer, ~60 mAh
- **LDO Regulators:** For analog circuits
- **Buck Converter:** For digital core (efficiency)
- **Charge Controller:** Manages charging current

### Power Domains
```
┌─ Core (BR28 Processor)
├─ Digital (Audio Codec, BLE)
├─ Analog (Mic amplifier, Speaker driver)
└─ Sensors (CTMU, ADC)
```

Each domain can be independently gated for power savings.

---

## Charging Workflow

```
AC Adapter Connected
        ↓
Charger IC Detection
        ↓
Current Limiting (~500 mA)
        ↓
Battery Voltage Monitoring
        ├─ 0-80%: Constant Current
        └─ 80-100%: Constant Voltage (Taper)
        ↓
Full Charge Detected (Thermal management)
        ↓
Trickle Charge (~10 mA maintenance)
```

**Configuration:** [→ GUI DOC TAB 06 - Volume Config](../GUI%20DOCUMENTATION/TAB%2006%20—%20Volume%20Config.md)

---

## Low Power Mode Optimization

### Touch Wake
```
Sleep State
    ↓
Touch Detected on PB1
    ↓
Wake Interrupt
    ↓
Resume to Active (< 100 ms)
```

### BT Wake
```
Sleep State
    ↓
BT Advertising Signal
    ↓
Resume to Low Power
    ↓
Active on connection
```

### Timeout Management
```
Idle for [configured time]
    ↓
Transition to Low Power
    ↓
Further idle → Sleep
```

---

## Power Configuration

```c
// In board_jl7016g_hybrid_cfg.h:
#define TCFG_POWER_LDO_MODE              1    // vs Buck mode
#define TCFG_CHARGE_TIMEOUT              180  // minutes
#define TCFG_LOW_POWER_TIMEOUT           30   // seconds idle
#define TCFG_SLEEP_TIMEOUT               120  // seconds in low power
```

---

## Optimization Techniques

| Technique | Benefit | Trade-off |
|-----------|---------|-----------|
| **Aggressive Gating** | 20% power reduction | May increase wake latency |
| **ANC Disable in Sleep** | 5% power saving | Requires user switch |
| **Reduced Sample Rate** | 10% power saving | Audio quality impact |
| **Low-latency BT** | Better responsiveness | Slightly higher power |

---

## Key Issues Fixed

| FIX | Issue | Solution |
|-----|-------|----------|
| **FIX-004** | PC5 Bias (Power) | Proper bias configuration |
| **FIX-012** | MIC Power PA0 | Switched to PA2 MICBIAS |

---

**Related Documentation:**
- [→ POWER DEEP DIVE](../UPDATE/DOC%20LIBRARY/POWER%20DEEP%20DIVE%20—%20Charging%20Wake,%20Low%20Power,%20and%20Reconnect%20Latency.md)
- [→ POWER PRIORITY 01](../UPDATE/DOC%20LIBRARY/POWER%20PRIORITY%2001%20—%20LDO%20vs%20Buck%20DC-DC%20on%20JL7016G%20Hybrid.md)
