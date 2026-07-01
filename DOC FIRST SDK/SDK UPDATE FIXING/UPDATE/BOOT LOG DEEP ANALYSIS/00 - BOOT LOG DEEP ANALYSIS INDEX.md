# Boot Log Deep Analysis Index

## Scope

This folder provides a deep technical explanation of the full runtime log you shared (power-on to Bluetooth/TWS/phone connection).

It covers:
- Clock and reset startup sequence
- Task scheduler creation and RTOS messages
- VM/BTIF mount and config loading
- USER_CFG parameter interpretation line-by-line
- TWS pairing, page scan, role switch, phone attach/detach
- Audio decoder/tone and UI transitions
- BLE advertising state changes
- Every error/warning-like line and whether it is critical
- Why your manual MAC did not appear in this specific capture

## Documents

| # | Document | Date | Time | Notes |
|---|---|---|---|---|
| 01 | [Chronological Line by Line Explanation](01%20-%20Chronological%20Line%20by%20Line%20Explanation.md) | 2026-04-28 | 15:42 | Full power-on to phone connect walkthrough |
| 02 | [Error Warning and Noise Decoder](02%20-%20Error%20Warning%20and%20Noise%20Decoder.md) | 2026-04-28 | 15:42 | Every warning/error line classified: real vs noise |
| 03 | [Left Right Provisioning Validation Against This Log](03%20-%20Left%20Right%20Provisioning%20Validation%20Against%20This%20Log.md) | 2026-04-28 | 15:42 | Verifies left/right MAC provisioning from runtime output |
| 04 | [Updated Log After MAC Implementation - Full Deep Explanation](04%20-%20UPDATED%20LOG%20AFTER%20MAC%20IMPLEMENTATION%20-%20FULL%20DEEP%20EXPLANATION.md) | 2026-04-28 | 15:42 | Post-MAC flash capture; first time provisioned address appears |
| 05 | [PC5 Pull Up Pull Down Decision](05%20-%20PC5%20Pull%20Up%20Pull%20Down%20Decision.md) | 2026-04-28 | 15:42 | External pull bias requirement for channel select |
| 06 | [Updated Log 2 - Left Bud Validation and Final Fix](06%20-%20UPDATED%20LOG%202%20-%20LEFT%20BUD%20VALIDATION%20AND%20FINAL%20FIX.md) | 2026-04-28 | 15:42 | Left bud confirmed; FIX-019 PC3 active-low resolved |
| 07 | [Updated Log 3 - MAC Verified + ADV Volume Behavior](07%20-%20UPDATED%20LOG%203%20-%20MAC%20VERIFIED%20+%20ADV%20VOLUME%20BEHAVIOR.md) | 2026-04-28 | 15:42 | MAC stable in runtime; ADV/volume ceiling behavior documented |
| 08 | [Boot Loop Exception Log - ANC Init Crash and Recovery](08%20-%20BOOT%20LOOP%20EXCEPTION%20LOG%20-%20ANC%20Init%20Crash%20and%20Recovery.md) | 2026-06-09 | — | 🔴 CRITICAL: Infinite exception boot loop — P11 heap (14.6 KB) exhausted after ANC gain load; `soft_reset_exception` every cycle; device recovered |

## Quick Conclusion for Your Current Log

- Latest captures are operational (boot, TWS establish, phone connect, A2DP start).
- Manual MAC provisioning is now validated in runtime address output.
- TWS is functional but still not fully seamless during some transition windows.
- Project requirement: PC5 pull bias is mandatory and must stay in hardware validation checklist.
- **2026-06-09:** Boot loop exception incident (doc 08) — caused by insufficient P11 heap (14.6 KB) exhausted during ANC init + BT stack allocation. Device recovered. Heap budget must be considered before enabling additional features.
