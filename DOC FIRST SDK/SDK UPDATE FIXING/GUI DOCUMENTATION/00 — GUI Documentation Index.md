# 00 — GUI Documentation Index

**Tool:** SDK_Config v2.0.47 · earphone-1.2.0  
**Chip:** AC701N / BR28  
**Workspace:** `D:\jl7016g final approach\SDKS\FIRST PERIORITY SDK`  
**Config binary:** `cpu/br28/tools/cfg_tool.bin` (embedded in firmware at build time)  
**Config state reference:** `cpu/br28/tools/cfg_tool_state_complete.lua` (read-only snapshot)

---

## About This Documentation

This folder documents every tab and every configurable field in the **SDK_Config GUI tool** (also called `luaconfig`). For each tab you will find:

- A **screenshot** of the tab as it was when the project was set up
- A **field reference table** with the current value of every setting
- An **SDK Configuration Status** section that tells you which settings are actually active in firmware vs. stored but unused

This is meant as a definitive reference — whenever you need to know what a setting does or whether it's currently wired up to firmware code, check here first.

### Fast Use Lanes

| I want to... | Open this page first |
|--------------|----------------------|
| Fix Bluetooth identity/name/MAC behavior | [TAB 01 — BT Config](TAB%2001%20%E2%80%94%20BT%20Config.md) |
| Tune call clarity/noise/echo behavior | [TAB 03 — Call Config](TAB%2003%20%E2%80%94%20Call%20Config.md) |
| Tune microphone electrical setup | [TAB 04 — Microphone Config](TAB%2004%20%E2%80%94%20Microphone%20Config.md) |
| Change power prompts and tones | [TAB 05 — Tone File Config](TAB%2005%20%E2%80%94%20Tone%20File%20Config.md) |
| Tune ANC gains and suppression | [TAB 07 — ANC Config](TAB%2007%20%E2%80%94%20ANC%20Config.md) |
| Validate metadata/checksum behavior | [TAB 08 — Device Info](TAB%2008%20%E2%80%94%20Device%20Info.md) |

---

## Folder Structure

```
GUI DOCUMENTATION/
├── 00 — GUI Documentation Index.md    ← This file
├── TAB 01 — BT Config.md
├── TAB 02 — Common Config.md
├── TAB 03 — Call Config.md
├── TAB 04 — Microphone Config.md
├── TAB 05 — Tone File Config.md
├── TAB 06 — Volume Config.md
├── TAB 07 — ANC Config.md
├── TAB 08 — Device Info.md
└── ASSETS/
    ├── TAB01-BT-Config.png
    ├── TAB02-Common-Status-Config.png
    ├── TAB02-Common-Key-Msg-Config.png
    ├── TAB02-Common-Charge-Config.png
    ├── TAB02-Common-Builtin-Touch-Config.png
    ├── TAB03-Call-Config.png
    ├── TAB04-Microphone-Config.png
    ├── TAB05-Tone-File-Config.png
    ├── TAB06-Volume-Config-Top.png
    ├── TAB06-Volume-Config-Bottom.png
    ├── TAB07-ANC-Config-Common-Gains.png
    ├── TAB07-ANC-Config-DRC.png
    ├── TAB07-ANC-Config-AHS.png
    └── TAB08-Device-Info.png
```

---

## Tab Pages

| #   | Tab Name              | Sub-Tabs                                                           | Screenshot       | Page                                                                        |
| --- | --------------------- | ------------------------------------------------------------------ | ---------------- | --------------------------------------------------------------------------- |
| 01  | **BT Config**         | —                                                                  | ✅                | [TAB 01 — BT Config](TAB%2001%20%E2%80%94%20BT%20Config.md)                 |
| 02  | **Common Config**     | Status Config, Key Msg Config, Charge Config, Builtin Touch Config | ✅ (×4)           | [TAB 02 — Common Config](TAB%2002%20%E2%80%94%20Common%20Config.md)         |
| 03  | **Call Config**       | Single MIC, Dual MIC, Triple MIC panels                            | ✅                | [TAB 03 — Call Config](TAB%2003%20%E2%80%94%20Call%20Config.md)             |
| 04  | **Microphone Config** | —                                                                  | ✅                | [TAB 04 — Microphone Config](TAB%2004%20%E2%80%94%20Microphone%20Config.md) |
| 05  | **Tone File Config**  | —                                                                  | ✅                | [TAB 05 — Tone File Config](TAB%2005%20%E2%80%94%20Tone%20File%20Config.md) |
| 06  | **Volume Config**     | System Volume, Call Volume                                         | ✅ (×2)           | [TAB 06 — Volume Config](TAB%2006%20%E2%80%94%20Volume%20Config.md)         |
| 07  | **ANC Config**        | Common Gains, DRC, AHS                                             | ✅ (×3)           | [TAB 07 — ANC Config](TAB%2007%20%E2%80%94%20ANC%20Config.md)               |
| 08  | **Device Info**       | —                                                                  | ✅                | [TAB 08 — Device Info](TAB%2008%20%E2%80%94%20Device%20Info.md)             |

---

## Quick Summary: Active Settings at a Glance

| Tab | Key Active Settings | Key Inactive Settings |
|-----|--------------------|-----------------------|
| **BT Config** | BT name "Buddie", BLE name "Buddie", BLE MAC (user-set), RF power HIGH, TWS pair code, auto-shutdown 5 min | Manual BT MAC (using derived/default) |
| **Common Config** | All LED + tone assignments, charge config (50mA/4.2V/10mA cutoff), low-power at 3.4V, power-off at 3.3V | Key Msg mappings (all null), LP Touch Key (OFF) |
| **Call Config** | NS, AGC, NLP, EQ all ON; MIC gain 8, ANS with aggress=1.25 | AEC disabled (cvpAEC=0); 2-mic and 3-mic params unused |
| **Microphone Config** | MIC_CAP_DIFF_MODE, 2.0K bias, 2.4V LDO — all active | — |
| **Tone File Config** | All 24 tone slots assigned → all packed into firmware | ANC tones only fire if ANC is enabled |
| **Volume Config** | 31-level system volume table, 15-level call volume table, Combined Volume mode | Fixed Analog Gain OFF; Generate button not yet run → output table shows zeros |
| **ANC Config** | All gains (unity), cmp_en, AHS enabled | DRC disabled (drc_en=0); entire tab conditional on CONFIG_ANC_ENABLE |
| **Device Info** | — (will be populated on next Save) | All empty — no checksum, no VID/PID, no version lock |

---

## Key Config IDs (syscfg_read)

| ID | What it reads | Tab |
|----|--------------|-----|
| `CFG_BT_NAME` | Bluetooth classic name | TAB 01 |
| `CFG_BLE_NAME` | BLE advertisement name | TAB 01 |
| `CFG_BT_MAC_ADDR` | BT MAC address | TAB 01 |
| `CFG_BLE_MAC_ADDR` | BLE MAC address | TAB 01 |
| `CFG_BT_RF_POWER_ID` | RF transmit power level | TAB 01 |
| `CFG_TWS_PAIR_CODE` | TWS pairing code | TAB 01 |
| `CFG_AUTO_SHUTDOWN` | Auto-shutdown timer | TAB 01 |
| `CFG_CHARGE_ID` | Charge voltage/current/thresholds | TAB 02 |
| `CFG_MIC_ID` | Microphone mode + LDO settings | TAB 04 |
| `CFG_TONE_ID` | Tone file pack | TAB 05 |
| `CFG_SYS_VOL_ID` | System (music) volume table | TAB 06 |
| `CFG_CALL_VOL_ID` | Call volume table | TAB 06 |
| `CFG_AEC_ID` | CVP / call processing params | TAB 03 |
| `CFG_ANC_ID` | ANC gains + AHS + DRC | TAB 07 |
| `CFG_LRC_ID` | Left/Right channel assignment | TAB 01 |

---

## Related Documentation

- [CONFIG GUI FIELD REFERENCE — Every Tab Every Option Explained.md](../UPDATE/DOC%20LIBRARY/CONFIG%20GUI%20FIELD%20REFERENCE%20%E2%80%94%20Every%20Tab%20Every%20Option%20Explained.md) — standalone field-by-field reference (created in prior session)
- FIX-001 through FIX-006 — Bug fix notes in `SDK UPDATE FIXING/`
