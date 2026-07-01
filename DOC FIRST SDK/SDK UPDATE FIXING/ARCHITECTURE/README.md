# 🏗️ System Architecture

**Purpose:** Understand the JL7016G hardware/software architecture, design patterns, and system interactions.

---

## 📊 Architecture Documentation

### Hardware Architecture
- **JL7016G Hybrid Processor** - Dual-core BR28 SoC, peripheral interfaces
- **Audio Codec System** - DAC/ADC configuration, audio signal flow
- **Touch Input System** - CTMU capacitive sensing, GPIO mapping
- **Power Management** - LDO vs Buck DC-DC, battery charging, low-power modes
- **Wireless Connectivity** - Bluetooth transceiver, antenna configuration

### Software Architecture
- **Event-Driven Model** - Touch events, audio events, system notifications
- **Weak Function Overrides** - Non-intrusive feature injection pattern
- **Configuration Layer** - Preprocessor-based runtime configuration
- **State Machines** - TWS pairing, in-ear detection, call handling

### System Interactions
- **Touch Processing Pipeline** - CTMU → Event Handler → GPIO Output
- **Audio Processing** - Mic input → Codec → Speaker output → TWS stream
- **Power State Transitions** - Active → Low Power → Sleep
- **TWS Synchronization** - MAC provisioning, bud identity, seamless reconnection

---

## 🔗 Block Diagrams

**Main System Flow:**
```
┌─────────────────────────────────────────────────────┐
│           JL7016G Hybrid Earphone                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Touch Input    Audio Input    Power Input         │
│      ↓              ↓               ↓               │
│    [CTMU]      [ADC/Codec]     [Battery]           │
│      ↓              ↓               ↓               │
│  [Event]   →  [Audio Proc]  →  [Power Mgmt]      │
│      ↓              ↓               ↓               │
│    [GPIO]      [DAC/Codec]     [LED/Charger]      │
│      ↓              ↓               ↓               │
│    [LED]        [Speaker]      [Status]            │
│                                                     │
│  ↔ TWS/Bluetooth Link ↔                            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 Design Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Weak Override** | Non-intrusive hooks | Touch event remapping (FIX-015) |
| **Lazy Init** | Deferred initialization | GPIO setup on first use |
| **Preprocessor Gate** | Conditional compilation | Feature enable/disable (zero overhead) |
| **Channel Filter** | Input routing | PB1 sensor → PC3 LED |

---

## 📈 Signal Flow Examples

### Touch LED Feedback (FIX-015)
```
PB1 Touch Detected
    ↓
CTMU Interrupt
    ↓
lp_touch_key_event_remap() [weak override]
    ↓
Channel 1? → YES
    ↓
Event Type? → {CLICK, LONG, DOUBLE_CLICK}
    ↓
gpio_write(PC3, 1) [LED ON]
    ↓
Return TRUE [continue normal processing]
```

### TWS Audio Streaming
```
Local Mic Input
    ↓
Audio Codec (ADC)
    ↓
Audio Processing (Effects, ANC)
    ↓
Bluetooth Encoder
    ↓
TX → TWS/Remote Earphone
    ↓
RX Bluetooth Decoder
    ↓
Audio Codec (DAC)
    ↓
Speaker Output
```

---

## 🔐 Configuration Hierarchy

```
board_jl7016g_hybrid_cfg.h
    ├── Pin Definitions (GPIO, ADC, IIS)
    ├── Feature Enables (ANC, TWS, IQ Audio)
    ├── Touch Configuration (CTMU, channels, sensitivity)
    ├── Audio Configuration (codec, effects, sample rate)
    ├── Power Configuration (LDO/Buck, charging, timeout)
    └── Advanced Settings (debug, logging, optimization)
```

---

## ✨ Key Components

- **BR28 Core:** 32-bit ARM processor, dual-core capable
- **CTMU:** Capacitive Touch Mutual Unit, 5 channels (PB1-PB5)
- **Audio Codec:** High-quality DAC/ADC with effects engine
- **Bluetooth:** BLE 5.0+ transceiver with TWS support
- **Power Manager:** Battery charging, LDO/DC-DC switching, sleep modes

---

## 📚 Related Documentation

- **Deep Dives:** [→ UPDATE/DOC LIBRARY/](../UPDATE/DOC%20LIBRARY/)
- **Guides:** [→ GUIDES/](../GUIDES/)
- **Fixes:** [→ FIXING/](../FIXING/)

---

**Status:** ✅ Architecture Complete  
**Last Updated:** May 1, 2026
