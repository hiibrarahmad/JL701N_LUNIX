---
tags: [improvements, index, audio, connection, jl7016g, planning]
date: 2026-06-08
status: IN PROGRESS — ACTIVE PLANNING
---

# 🚀 JL7016G SDK — Improvements Index

> Planned improvements for audio quality and Bluetooth/TWS connection on the JL7016G Hybrid BR28 platform.
> All improvements are ranked by effort and risk. Start with **Low effort** items for immediate wins.
> Source of truth: [→ FEATURE AUDIT COMPLETE.md](./FEATURE%20AUDIT%20COMPLETE.md)

---

## Priority Matrix — Start Here

| Priority | ID | Title | Category | Effort | Risk | Impact |
|---|---|---|---|---|---|---|
| ⭐ 1 | [AUDIO-IMP-001](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-001%20—%20DRC%20Dynamic%20Range%20Compression.md) | DRC Dynamic Range Compression | Audio | 🟢 Low | ✅ Safe | High — prevents clipping, consistent loudness |
| ⭐ 2 | [AUDIO-IMP-004](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-004%20—%20Wind%20Noise%20Detection.md) | Wind Noise Detection | Audio | 🟢 Low | ✅ Safe | High — ANC quality outdoors |
| ⭐ 3 | [AUDIO-IMP-005](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-005%20—%20Speak-to-Chat%20Transparency%20Mode.md) | Speak-to-Chat Transparency | Audio | 🟢 Low | ✅ Safe | High — user experience |
| ⭐ 4 | [CONN-IMP-002](./CONNECTION%20IMPROVEMENTS/CONN-IMP-002%20—%20SPP%20Profile%20Enable.md) | SPP Profile Enable | Connection | 🟢 Low | ✅ Safe | Medium — debug + custom app channel |
| ⭐ 5 | [CONN-IMP-005](./CONNECTION%20IMPROVEMENTS/CONN-IMP-005%20—%20Auto-Shutdown%20Timer%20Tuning.md) | Auto-Shutdown Timer Tuning | Connection | 🟢 Low | ✅ Safe | Medium — UX + battery life |
| 6 | [AUDIO-IMP-009](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-009%20—%20MIC%20Gain%20Optimization.md) | MIC Gain Optimization | Audio | 🟢 Low | ✅ Safe | High — call clarity, ANC performance |
| 7 | [AUDIO-IMP-010](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-010%20—%20Volume%20Ceiling%20and%20ANC%20Cap%20Analysis.md) | Volume Ceiling Analysis | Audio | 🟢 Low | ⚠️ Test carefully | Medium — max loudness increase |
| 8 | [AUDIO-IMP-008](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-008%20—%20EQ%20Profile%20Reference%20and%20Tuning.md) | EQ Profile Reference | Audio | 🟢 Low | ✅ Safe | Medium — reference tuning guide |
| 9 | [CONN-IMP-003](./CONNECTION%20IMPROVEMENTS/CONN-IMP-003%20—%20PBAP%20Phone%20Book%20Access%20Profile.md) | PBAP Phone Book Profile | Connection | 🟢 Low | ✅ Safe | Low — caller ID display |
| 10 | [AUDIO-IMP-002](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-002%20—%20Dual-Mic%20ENC%20Call%20Quality.md) | Dual-Mic ENC Call Quality | Audio | 🟡 Medium | ⚠️ GPIO conflict check | High — call audio |
| 11 | [AUDIO-IMP-006](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-006%20—%20Adaptive%20ANC%20Ear-Canal%20Fit.md) | Adaptive ANC Ear-Canal Fit | Audio | 🟡 Medium | ⚠️ Calibration needed | High — ANC effectiveness |
| 12 | [CONN-IMP-004](./CONNECTION%20IMPROVEMENTS/CONN-IMP-004%20—%20Low%20Power%20Mode%20Enable.md) | Low Power Mode Enable | Connection | 🟡 Medium | ⚠️ Test reconnect latency | High — battery life |
| 13 | [CONN-IMP-006](./CONNECTION%20IMPROVEMENTS/CONN-IMP-006%20—%20TWS%20Sibling%20Reconnect%20Optimization.md) | TWS Sibling Reconnect Speed | Connection | 🟡 Medium | ⚠️ TWS stability | High — connection UX |
| 14 | [CONN-IMP-007](./CONNECTION%20IMPROVEMENTS/CONN-IMP-007%20—%20BT%20Clock%20Frequency%20Optimization.md) | BT Clock Power vs Performance | Connection | 🟡 Medium | ⚠️ Test each mode | Medium — battery/latency |
| 15 | [AUDIO-IMP-003](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-003%20—%20ANC%20Right%20Channel%20Extension.md) | ANC Right Channel Extension | Audio | 🔴 High | 🔴 Hardware required | High — true stereo ANC |
| 16 | [CONN-IMP-001](./CONNECTION%20IMPROVEMENTS/CONN-IMP-001%20—%20Simultaneous%20TWS%20OTA%20Double-Bank%20Flash.md) | Simultaneous TWS OTA | Connection | 🔴 High | 🔴 2 MB flash needed | High — production OTA |
| 17 | [AUDIO-IMP-007](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-007%20—%20LC3%20Codec%20LE%20Audio.md) | LC3 Codec / LE Audio | Audio | 🔴 High | 🔴 Stack + flash constraint | High — future-proofing |

---

## By Category

### 🔊 Audio Improvements (10 items)
→ [AUDIO IMPROVEMENTS/README.md](./AUDIO%20IMPROVEMENTS/README.md)

| ID | Title | Effort | Risk |
|---|---|---|---|
| [AUDIO-IMP-001](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-001%20—%20DRC%20Dynamic%20Range%20Compression.md) | DRC Dynamic Range Compression | 🟢 Low | ✅ Safe |
| [AUDIO-IMP-002](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-002%20—%20Dual-Mic%20ENC%20Call%20Quality.md) | Dual-Mic ENC Call Quality | 🟡 Medium | ⚠️ Check PA4 conflict |
| [AUDIO-IMP-003](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-003%20—%20ANC%20Right%20Channel%20Extension.md) | ANC Right Channel Extension | 🔴 High | 🔴 Hardware |
| [AUDIO-IMP-004](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-004%20—%20Wind%20Noise%20Detection.md) | Wind Noise Detection | 🟢 Low | ✅ Safe |
| [AUDIO-IMP-005](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-005%20—%20Speak-to-Chat%20Transparency%20Mode.md) | Speak-to-Chat Transparency Mode | 🟢 Low | ✅ Safe |
| [AUDIO-IMP-006](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-006%20—%20Adaptive%20ANC%20Ear-Canal%20Fit.md) | Adaptive ANC Ear-Canal Fit | 🟡 Medium | ⚠️ Calibration |
| [AUDIO-IMP-007](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-007%20—%20LC3%20Codec%20LE%20Audio.md) | LC3 Codec / LE Audio | 🔴 High | 🔴 Flash + stack |
| [AUDIO-IMP-008](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-008%20—%20EQ%20Profile%20Reference%20and%20Tuning.md) | EQ Profile Reference and Tuning | 🟢 Low | ✅ Safe |
| [AUDIO-IMP-009](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-009%20—%20MIC%20Gain%20Optimization.md) | MIC Gain Optimization | 🟢 Low | ✅ Safe |
| [AUDIO-IMP-010](./AUDIO%20IMPROVEMENTS/AUDIO-IMP-010%20—%20Volume%20Ceiling%20and%20ANC%20Cap%20Analysis.md) | Volume Ceiling and ANC Cap Analysis | 🟢 Low | ⚠️ Test loudness |

### 📡 Connection Improvements (7 items)
→ [CONNECTION IMPROVEMENTS/README.md](./CONNECTION%20IMPROVEMENTS/README.md)

| ID | Title | Effort | Risk |
|---|---|---|---|
| [CONN-IMP-001](./CONNECTION%20IMPROVEMENTS/CONN-IMP-001%20—%20Simultaneous%20TWS%20OTA%20Double-Bank%20Flash.md) | Simultaneous TWS OTA (Double-Bank) | 🔴 High | 🔴 Needs 2 MB flash |
| [CONN-IMP-002](./CONNECTION%20IMPROVEMENTS/CONN-IMP-002%20—%20SPP%20Profile%20Enable.md) | SPP Profile Enable | 🟢 Low | ✅ Safe |
| [CONN-IMP-003](./CONNECTION%20IMPROVEMENTS/CONN-IMP-003%20—%20PBAP%20Phone%20Book%20Access%20Profile.md) | PBAP Phone Book Profile | 🟢 Low | ✅ Safe |
| [CONN-IMP-004](./CONNECTION%20IMPROVEMENTS/CONN-IMP-004%20—%20Low%20Power%20Mode%20Enable.md) | Low Power Mode Enable | 🟡 Medium | ⚠️ Reconnect latency |
| [CONN-IMP-005](./CONNECTION%20IMPROVEMENTS/CONN-IMP-005%20—%20Auto-Shutdown%20Timer%20Tuning.md) | Auto-Shutdown Timer Tuning | 🟢 Low | ✅ Safe |
| [CONN-IMP-006](./CONNECTION%20IMPROVEMENTS/CONN-IMP-006%20—%20TWS%20Sibling%20Reconnect%20Optimization.md) | TWS Sibling Reconnect Optimization | 🟡 Medium | ⚠️ TWS stability |
| [CONN-IMP-007](./CONNECTION%20IMPROVEMENTS/CONN-IMP-007%20—%20BT%20Clock%20Frequency%20Power%20vs%20Performance.md) | BT Clock Frequency Optimization | 🟡 Medium | ⚠️ Per-mode testing |

---

## Related Docs

- [→ FEATURE AUDIT COMPLETE.md](./FEATURE%20AUDIT%20COMPLETE.md) — All flags: enabled, disabled, out-of-scope
- [→ AUDIO DEEP DIVE](../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/AUDIO%20DEEP%20DIVE.md)
- [→ TWS DEEP DIVE](../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/TWS%20DEEP%20DIVE.md)
- [→ POWER DEEP DIVE](../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/POWER%20DEEP%20DIVE.md)
- [→ TODO-BACKLOG](../SDK%20UPDATE%20FIXING/UPDATE/TODO-BACKLOG.md)
- [→ Existing Feature Audit](../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/FEATURE%20AUDIT.md)
