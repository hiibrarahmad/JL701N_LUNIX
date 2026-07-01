---
tags: [guide, troubleshooting, build-errors, solutions]
date: 2026-05-05
difficulty: intermediate
---

# Troubleshooting — JL7016G Hybrid SDK

**Time:** Variable | **Difficulty:** Intermediate

---

## Decision Tree — Start Here

Use this flowchart to find the right fix quickly. Work top-to-bottom until you find your symptom.

```
SYMPTOM
├── Build / Compile Error?
│   ├── "'TCFG_...' undeclared"         → FIX-001
│   ├── "undefined reference to lis2de12" → FIX-002
│   └── "undefined reference to online_db / fft_pca" → FIX-003
│
├── Device won't boot / silent?
│   ├── UART output visible? YES → Boot Loop Analysis (see below)
│   └── UART output visible? NO → Check flash / UART baud rate (FIX-011)
│
├── Wrong BT name or MAC?
│   ├── Shows "Buddie" regardless of Config GUI setting → FIX-006
│   └── BLE MAC address wrong after flash → FIX-005
│
├── TWS (True Wireless Stereo) problem?
│   ├── Buds won't pair / one bud only → FIX-004, FIX-014
│   ├── Volume difference between buds → FIX-020
│   ├── Both buds do same action (both Vol Up, or both Next) → FIX-022
│   ├── Volume oscillates rapidly during hold → FIX-022
│   └── Per-bud compile-time key split has no effect → FIX-021
│
├── Touch (PB4 / CH3) not working?
│   ├── Touch detected in logs but no media action → FIX-007
│   ├── Long-press / hold never fires → FIX-008
│   ├── "invalid touch value" in logs → FIX-009
│   └── Touch event intercepted by in-ear logic → FIX-010
│
├── Touch (PB1 / CH1) problem?
│   ├── PB1 touch fires play/pause/next → FIX-018
│   ├── PB1 hold triggers power-off → FIX-017
│   ├── PB1 touch not generating app key events (expected) → FIX-015, FIX-018
│   └── PC3 polarity is backwards (HIGH on touch, LOW at idle) → FIX-019
│
├── Microphone / Audio?
│   ├── MIC zero signal / no audio at all → FIX-012
│   └── MIC only picks up physical taps, not voice → FIX-013
│
└── UART output garbled / mixed with "uuu" characters?
    └── Wrong baud rate → FIX-011
```

---

## Build Errors

### Compilation Fails
**Check:** [→ FIXING/ Folder](../FIXING/)
- FIX-001 to FIX-014 cover most common errors
- Search for your error message in FIX records

### Undefined References
**Check:** Board configuration in `board_jl7016g_hybrid_cfg.h`
- Missing macro definitions
- Incorrect GPIO port assignments
- See FIX-001 for macro setup example

---

## Boot Issues

### Device Won't Boot
**Analyze:** [→ BOOT LOG DEEP ANALYSIS](../UPDATE/BOOT%20LOG%20DEEP%20ANALYSIS/)
- Chronological line-by-line log analysis
- Error and warning decoder
- Left-right provisioning validation

### MAC Address Issues
**Reference:** [→ MAC ADDRESS PROVISIONING](../UPDATE/MAC%20ADDRESS%20PROVISIONING/)
- Factory flash workflow
- Provisioning functions
- TWS sibling configuration

---

## TWS (True Wireless Stereo)

### Pairing Fails
**Solution:** [→ FIX-014](../FIXING/FIX-014%20—%20TWS%20not%20seamless%20under%20MAC%20profile%20and%20PC5%20bias%20requirement.md)

### Reconnection Issues
**Deep Dive:** [→ TWS DEEP DIVE](../UPDATE/DOC%20LIBRARY/TWS%20DEEP%20DIVE%20—%20Reconnect%20Lag,%20Bud%20Identity,%20MAC%20Strategy,%20and%20Risks.md)

---

## Power & Performance

### High Power Consumption
**Reference:** [→ POWER DEEP DIVE](../UPDATE/DOC%20LIBRARY/POWER%20DEEP%20DIVE%20—%20Charging%20Wake,%20Low%20Power,%20and%20Reconnect%20Latency.md)

### Slow Boot
**Check:** Boot log analysis and startup optimization

---

## Getting Help

1. **Understand the system:** [→ ARCHITECTURE/](../ARCHITECTURE/)
2. **Check existing fixes:** [→ FIXING/](../FIXING/)
3. **Deep dive on topic:** [→ UPDATE/DOC LIBRARY/](../UPDATE/DOC%20LIBRARY/)
4. **Reference specifications:** [→ REFERENCE/](../REFERENCE/)

---

**Return to:** [→ Main Documentation Hub](../README.md)
