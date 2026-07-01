# Reference & Specifications

**Purpose:** API references, technical specifications, and quick lookup resources.

---

## Files in This Folder

| File | Description |
|------|-------------|
| [GLOSSARY.md](./GLOSSARY.md) | Alphabetical acronym and abbreviation reference for all terms used in this vault |
| [QUICK_REFERENCE.txt](./QUICK_REFERENCE.txt) | Quick lookup — key macros, pin assignments, API signatures |
| [CH1_PROCESSING_PROOF.md](./CH1_PROCESSING_PROOF.md) | **PB1-specific** — Proof-of-concept trace showing CH1 event processing flow |
| [CODE_EXECUTION_TRACE.md](./CODE_EXECUTION_TRACE.md) | **PB1-specific** — Detailed code path trace for PB1/CH1 bring-up debugging |
| [README_PB1_FIX.md](./README_PB1_FIX.md) | **PB1-specific** — Summary of PB1 fix approach and validation steps |
| [README_PB1_IMPLEMENTATION.md](./README_PB1_IMPLEMENTATION.md) | **PB1-specific** — Implementation notes for the PB1 complete solution |
| [simulate_event_flow.py](./simulate_event_flow.py) | **PB1-specific** — Python script simulating the CH1 event flow for validation |
| [validate_logic.py](./validate_logic.py) | **PB1-specific** — Python script validating PB1 touch logic conditions |

> **Note:** The four `README_PB1_*`, `CH1_*`, `CODE_*`, and `*.py` files were generated during the PB1 / FIX-015 bring-up investigation. They are preserved here as a debugging record. For the official fix documentation, see [FIX-015](../FIXING/FIX-015%20—%20PB1_COMPLETE_SOLUTION.md) and [FIX-018](../FIXING/FIX-018%20—%20PB1%20Key%20Events%20Suppressed%20GPIO%20Only.md).

---

## 📖 Available References

### GPIO & Hardware APIs
- GPIO driver functions and pin definitions
- ADC configuration and sampling
- IIS audio interface specifications
- CTMU touch sensor APIs

### Software APIs
- Event system and event types
- Weak function override mechanisms
- Configuration macros and symbols
- Build symbols and compiler options

### Hardware Specifications
- JL7016G Hybrid SoC datasheet summary
- Peripheral pinout and capabilities
- Electrical specifications (voltage, current, power)
- Timing requirements and latencies

### Software Specifications
- Build system and compilation flow
- Memory layout and allocation
- Stack and heap usage
- Performance characteristics

---

## 🔗 Quick Lookup

### By Component
- **Touch System:** CTMU configuration, channel mapping, event handling
- **Audio:** Codec settings, sample rates, streaming protocols
- **Power:** Sleep modes, wake signals, charging profiles
- **Wireless:** Bluetooth profiles, TWS protocols, MAC addressing

### By Operation
- **Initialization:** Boot sequence, hardware setup, feature enablement
- **Configuration:** Board config, GUI settings, runtime parameters
- **Execution:** Event processing, real-time operation, state transitions
- **Debug:** Logging, UART output, error codes

---

## 📊 API Quick Reference

| Category | Function | File |
|----------|----------|------|
| **GPIO** | `gpio_direction_output()` | driver/gpio.h |
| **GPIO** | `gpio_write()` | driver/gpio.h |
| **Events** | `sys_event` structure | system/event.h |
| **Touch** | `lp_touch_key_event_remap()` | cpu/br28/lp_touch_key.c |
| **Config** | `TCFG_*` macros | board/br28/board_*_cfg.h |

---

## 📈 Performance Specs

| Metric | Value |
|--------|-------|
| GPIO Write Latency | ~200 ns |
| Touch Event Latency | < 1 ms |
| Boot Time | ~2-5 seconds |
| Code Size (Full Build) | ~500 KB |
| RAM Usage | ~100 KB |
| Power (Active) | ~50 mA |
| Power (Sleep) | ~5 μA |

---

## 🔐 Configuration Macros

### Enable/Disable Pattern
```c
#define TCFG_FEATURE_ENABLE    ENABLE_THIS_MOUDLE  // Compiles in feature
// or
#define TCFG_FEATURE_ENABLE    DISABLE_THIS_MOUDLE // Compiles out feature (zero overhead)
```

### GPIO Configuration Pattern
```c
#define TCFG_FEATURE_PORT      IO_PORTC_03        // GPIO port selection
#define TCFG_FEATURE_ACTIVE    1                  // Active level (0 or 1)
```

---

## 📚 Related Documentation

- **Architecture:** [→ ARCHITECTURE/](../ARCHITECTURE/)
- **Guides:** [→ GUIDES/](../GUIDES/)
- **Deep Dives:** [→ UPDATE/DOC LIBRARY/](../UPDATE/DOC%20LIBRARY/)

---

**Status:** ✅ References Available  
**Last Updated:** May 1, 2026
