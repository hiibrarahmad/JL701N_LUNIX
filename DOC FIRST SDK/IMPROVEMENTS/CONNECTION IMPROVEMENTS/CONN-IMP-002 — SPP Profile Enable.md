---
tags: [connection, bluetooth, spp, serial, profile, debug, jl7016g, improvement]
date: 2026-06-08
status: PLANNED — NOT IMPLEMENTED
effort: 🟢 Low
risk: ✅ Safe — additive profile, no impact on existing A2DP/HFP
priority: ⭐ 4 — Low effort, enables debug channel and custom app communication
---

# 📡 CONN-IMP-002 — SPP Profile Enable

> **One-line summary:** Enable the Serial Port Profile (SPP) to open a Bluetooth RFCOMM serial channel between the earphone and a phone or PC — useful for diagnostics, firmware configuration via custom app, ANC tuning, and custom data protocols.

---

## Current State

SPP is **disabled**:

```c
// board_jl7016g_hybrid_cfg.h
#define USER_SUPPORT_PROFILE_SPP    0   // Serial Port Profile off
```

Currently the only data channel to the earphone (beyond A2DP audio and HFP calls) is:
- **BLE RCSP** — Jieli proprietary protocol for OTA + basic config
- **BLE GATT custom** — if `JL_EARPHONE_APP_EN=1` is used

SPP adds a classic Bluetooth (BR/EDR) serial pipe that is easy to use from Android apps (`BluetoothSocket`) and PC tools (`RFCOMM` terminal).

---

## What SPP Enables

| Use Case | Details |
|---|---|
| **ANC tuning tool** | If `TCFG_ANC_TOOL_DEBUG_ONLINE=ENABLE`, SPP is the transport for the PC-side ANC tool |
| **Custom diagnostics** | Send UART-style debug output over BT to a phone/PC without physical cable |
| **Config protocol** | A custom Android app can send config commands (EQ settings, gain, ANC mode) |
| **Production testing** | Factory test jig communicates with earphone via SPP to verify audio levels |
| **AEC tuning** | `TCFG_AEC_TOOL_ONLINE_ENABLE` also uses SPP as transport |

---

## Recommended Change

```c
// board_jl7016g_hybrid_cfg.h
#define USER_SUPPORT_PROFILE_SPP    1   // was 0
```

No other config changes required. SPP is implemented in the BT stack — enabling the flag links the RFCOMM layer.

### Impact on Existing Profiles

| Profile | Effect of Adding SPP |
|---|---|
| A2DP (music) | No impact |
| HFP (calls) | No impact |
| HID | No impact |
| BLE RCSP | No impact — SPP is classic BT, RCSP is BLE |

### Page Count Consideration

Adding SPP adds one more SDP service record. The `TCFG_BD_NUM=1` (one phone connection in TWS mode) is unchanged — SPP connects from the **same already-paired phone**. No additional device slots needed.

---

## SPP Usage on Android

```java
// Minimal Android SPP client
BluetoothDevice device = ...;
BluetoothSocket socket = device.createRfcommSocketToServiceRecord(MY_UUID);
socket.connect();
OutputStream out = socket.getOutputStream();
out.write("AT+GAIN=8\r\n".getBytes());
```

UUID for SPP: `00001101-0000-1000-8000-00805F9B34FB` (standard SPP UUID).

---

## Risk & Trade-offs

| Aspect | Assessment |
|---|---|
| Flash cost | ~2–4 KB for RFCOMM layer — negligible at 1 MB |
| Pairing compatibility | Works with all Android 5.0+ and Windows 10+ |
| Security | SPP has no PIN in BR/EDR — rely on BT pairing for access control |
| Battery impact | < 1% — RFCOMM only active when data is flowing |
| Reversible | Yes — set `0` to disable |

---

## Verification Steps

1. Enable flag and rebuild
2. Flash to test bud
3. Pair with Android phone
4. Open Bluetooth settings → paired devices → connect
5. Use a BT serial terminal app (e.g., "Serial Bluetooth Terminal") to connect to SPP service
6. Confirm connection established: app shows "Connected"
7. Send a test byte — verify no error on earphone side (UART log should not show SPP error)

---

## Related
- [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md) — Section 5
- [→ AUDIO-IMP-008 EQ Tuning](../AUDIO%20IMPROVEMENTS/AUDIO-IMP-008%20—%20EQ%20Profile%20Reference%20and%20Tuning.md) — SPP enables live ANC/EQ tool
- [→ GUI TAB 01 — BT Config](../../SDK%20UPDATE%20FIXING/GUI%20DOCUMENTATION/TAB%2001%20—%20BT%20Config.md)
- [→ BT_CONFIG Structure](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/BT_CONFIG%20-%20Bluetooth%20Configuration%20Structure.md)
