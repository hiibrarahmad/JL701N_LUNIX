---
tags: [guide, configuration, ac701n, tool]
date: 2026-05-01
difficulty: beginner
---

# ⚙️ Device Configuration Guide

**Time:** 10 minutes | **Difficulty:** Beginner

---

## AC701N Configuration Tool Overview

The AC701N tool is a GUI-based configuration manager for the JL7016G earphone firmware.

---

## Configuration Workflow

### 1. Open Configuration Tool
```
Launch AC701N application
Select: JL7016G Hybrid board
Connect: USB to development kit
```

### 2. Navigate Tabs
The tool has **8 main configuration tabs**:

| Tab | Purpose |
|-----|---------|
| **TAB 01** | Bluetooth configuration (profiles, names) |
| **TAB 02** | Common settings (device-wide options) |
| **TAB 03** | Call handling (call routing, audio) |
| **TAB 04** | Microphone setup (mic selection, gain) |
| **TAB 05** | Tone file management (alert sounds) |
| **TAB 06** | Volume levels (all audio paths) |
| **TAB 07** | ANC settings (noise cancellation) |
| **TAB 08** | Device information (board, version) |

### 3. Apply Changes
```
Review settings
Click: [Apply] or [Upload to Device]
Wait for confirmation
```

---

## Common Configuration Tasks

### Enable ANC
**TAB 07** → ANC Enable → Save

### Change Device Name
**TAB 02** → Device Name → Enter new name → Apply

### Configure MAC Address
**TAB 02** → MAC Configuration → Set addresses → Save

---

## Where to Find Detailed Docs

→ **[GUI DOCUMENTATION/](../GUI%20DOCUMENTATION/)**

Each tab has dedicated documentation with:
- Field descriptions
- Valid value ranges
- Common settings
- Troubleshooting tips

---

**Next Step:** [→ MAC Address Configuration](../UPDATE/MAC%20ADDRESS%20PROVISIONING/)
