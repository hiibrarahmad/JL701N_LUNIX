---
tags: [connection, tws, reconnect, sibling, latency, bluetooth, jl7016g, improvement]
date: 2026-06-08
status: PLANNED — TEST BEFORE CHANGING
effort: 🟡 Medium
risk: ⚠️ TWS stability — test with multiple reconnect scenarios
priority: 13 — Medium effort, high user-visible impact
---

# 📡 CONN-IMP-006 — TWS Sibling Reconnect Optimization

> **One-line summary:** Analyze and optimize the TWS sibling discovery and reconnect sequence. Currently the sibling timeout is 4 seconds and there is no documented behavior for what happens when one bud powers on significantly later than the other.

---

## Current State

```c
// board_jl7016g_hybrid_cfg.h
#define CONFIG_TWS_CONNECT_SIBLING_TIMEOUT    4    // seconds
#define CONFIG_TWS_AUTO_PAIR_WITHOUT_UNPAIR   1    // re-pair without explicit unlink
#define CONFIG_TWS_POWEROFF_SAME_TIME         1    // both buds shut down together
```

### Current TWS Boot Sequence

```
Both buds powered on (case opened)
    │
    ├─ Left bud scans for right bud (4s window)
    └─ Right bud scans for left bud (4s window)
    
Both buds find each other within 4s → TWS connected
    │
    └─ Both buds scan for phone → phone connects → audio streaming
```

---

## Problem Scenarios

### Scenario 1 — Staggered Boot (One Bud Picked Up Later)

If the user picks up the left bud first and the right bud 5–10 seconds later:
- Left bud's 4s sibling window expires → left goes to solo mode → connects to phone alone
- Right bud boots → cannot find left bud in sibling window (left already connected to phone)
- Result: Right bud operates as an independent earphone, not TWS

**User experience:** One ear has music, the other is silent or beeping "connecting."

### Scenario 2 — Temporary Loss of TWS Link (Momentary Separation)

If the user moves the buds apart momentarily (takes one out to speak to someone):
- TWS link drops
- `CONFIG_TWS_CONNECT_SIBLING_TIMEOUT = 4s` — if reinsertion > 4s, solo mode kicks in
- Music plays only in the remaining bud

### Scenario 3 — Fast Sibling Boot After Case Insert

If both buds are re-inserted simultaneously into the case and immediately removed:
- Both may boot at nearly the same millisecond
- RF collision during initial scan is possible if both transmit BT scan at same time
- This can cause one scan to fail, forcing one bud to retry

---

## Recommended Optimizations

### Optimization 1 — Extend Sibling Timeout

```c
// board_jl7016g_hybrid_cfg.h
#define CONFIG_TWS_CONNECT_SIBLING_TIMEOUT    8    // was 4 seconds → double to 8
```

**Trade-off:** If the sibling is genuinely off or missing, solo mode starts 4 seconds later — acceptable for a user who only has one bud.

### Optimization 2 — Verify Re-scan After Phone Connection

The SDK's `CONFIG_TWS_AUTO_PAIR_WITHOUT_UNPAIR=1` should allow the late-joining bud to reconnect to its sibling even after the sibling is already connected to the phone. Verify in the source (`bt_tws.c`): look for `tws_reconnect` or `tws_scan_after_connect` behavior.

If re-scan is not implemented: request from Jieli SDK support, or check SDK change log for `tws_slave_reconnect` functionality.

### Optimization 3 — Jitter on Boot Scan Start

Some TWS implementations add a small random delay (0–100 ms) before the first sibling scan to reduce RF collision probability:

```c
// Example pseudo-code in bt_tws.c init:
u32 jitter_ms = (get_chip_id() & 0xFF) % 100;  // 0–100 ms based on chip ID
sys_timer_add(jitter_ms, tws_sibling_scan_start, ...);
```

Check if the JL SDK already does this — if not, it is a low-risk addition.

---

## TWS Connection Architecture (Reference)

```
Left Bud (Master)           Right Bud (Slave)
    │                             │
    │← scan ──────────────────────│
    │         TWS BT link         │
    │────────────────────────────►│
    │                             │
    │← audio OPUS stream          │
    │────────────────────────────►│
    │                             │
Phone connects to Left (Master)
    │
    └─ Left distributes audio to Right via TWS OPUS link
```

The phone only ever sees and connects to the **master bud** (left, per PC5 pulldown). The right bud is transparent to the phone.

---

## Diagnosing Current Reconnect Behavior

Enable UART logging (`TCFG_UART0_ENABLE=ENABLE`, PB5 at 115200 baud) and monitor:

| Log Pattern | Meaning |
|---|---|
| `tws scan start` | Sibling scan beginning |
| `tws found sibling` | Sibling discovered |
| `tws connect ok` | TWS link established |
| `tws timeout, solo mode` | Sibling not found in timeout window |
| `tws reconnect attempt` | Late sibling trying to rejoin |

Capture logs for each reconnect scenario above, then tune the timeout accordingly.

---

## Risk & Trade-offs

| Aspect | Assessment |
|---|---|
| Longer timeout = longer solo-mode delay | 8s vs 4s — barely noticeable to user |
| Re-scan implementation complexity | If not in SDK, may require Jieli support |
| TWS stability after change | Must test 10+ reconnect cycles for each scenario |
| `CONFIG_TWS_POWEROFF_SAME_TIME=1` interaction | If both buds shut down together, staggered boot is less common |
| Reversible | Yes — revert constant and rebuild |

---

## Verification Test Matrix

| Test | Pass Criteria |
|---|---|
| Both buds removed simultaneously | TWS connected within 3 seconds |
| Left bud removed 5s before right | Both buds TWS-connected within 10s of right bud boot |
| One bud taken out during music | Remaining bud continues playing; other rejoins within 8s of reinsertion |
| 10× consecutive case close/open | All 10 result in successful TWS within 5s |
| Range test (separate buds 2m) | TWS link maintains; audio continues |

---

## Related
- [→ FEATURE AUDIT COMPLETE.md](../FEATURE%20AUDIT%20COMPLETE.md) — Section 5
- [→ TWS DEEP DIVE](../../SDK%20UPDATE%20FIXING/UPDATE/DOC%20LIBRARY/TWS%20DEEP%20DIVE.md)
- [→ FIX-004 TWS Auto Pairing](../../SDK%20UPDATE%20FIXING/FIXING/FIX-004%20—%20TWS%20auto%20pairing%20and%20PC5%20channel%20select%20validation.md)
- [→ FIX-014 TWS Seamless](../../SDK%20UPDATE%20FIXING/FIXING/FIX-014%20—%20TWS%20not%20seamless%20under%20MAC%20profile%20and%20PC5%20bias%20requirement.md)
- [→ CONN-IMP-005 Auto-Shutdown](./CONN-IMP-005%20—%20Auto-Shutdown%20Timer%20Tuning.md) — Shutdown timer and sibling timeout interact
