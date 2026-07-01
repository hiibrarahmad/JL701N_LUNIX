---
tags: [power, charging, low-power, wake, reconnect, latency, tws]
date: 2026-04-27
board: JL7016G Hybrid
chip: AC701N (BR28)
status: Documentation only - no code changes
---

# POWER DEEP DIVE - Charging Wake, Low Power, and Reconnect Latency

## Scope

This document explains the current power-related behavior that affects user experience on JL7016G Hybrid, especially:

1. What happens when a bud is inserted into or removed from the charger/case.
2. Why wake and reconnect can feel delayed even when TWS already works.
3. Which board-level macros control the current behavior.
4. What can be improved later without blindly changing a working build.

This is a design and risk study only. No firmware change is applied here.

---

## 1) Current Power Configuration Snapshot

Primary board config file:
- apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h

Current relevant power macros:

| Macro | Current value | Meaning |
|------|---------------|---------|
| `TCFG_LOWPOWER_POWER_SEL` | `PWR_LDO15` | System uses LDO power mode instead of DCDC |
| `TCFG_LOWPOWER_BTOSC_DISABLE` | `0` | BT oscillator is kept in low-power path |
| `TCFG_LOWPOWER_LOWPOWER_SEL` | `0` | Generic low-power entry is disabled in current board config |
| `TCFG_LOWPOWER_VDDIOM_LEVEL` | `VDDIOM_VOL_30V` | IO power domain at 3.0V |
| `TCFG_LOWPOWER_OSC_TYPE` | `OSC_TYPE_LRC` | Low-power oscillator source is LRC |
| `TCFG_LOWPOWER_RAM_SIZE` | `3` | Largest RAM retention/power-down footprint among current options |
| `TCFG_CHARGE_ENABLE` | `ENABLE_THIS_MOUDLE` | Internal charge support enabled |
| `TCFG_CHARGE_POWERON_ENABLE` | `DISABLE` | Charger insertion itself does not force normal power-on |
| `TCFG_CHARGESTORE_ENABLE` | `DISABLE_THIS_MOUDLE` | Generic smart chargestore path disabled |
| `TCFG_TEST_BOX_ENABLE` | `ENABLE_THIS_MOUDLE` | Test-box communication active |
| `TCFG_ANC_BOX_ENABLE` | `CONFIG_ANC_ENABLE` | ANC box support follows ANC enable |
| `TCFG_UMIDIGI_BOX_ENABLE` | `ENABLE_THIS_MOUDLE` | Vendor charge-box protocol enabled |

Important conclusion:

The board is not in a maximally aggressive low-power profile, but it still uses case/charge related logic and persistent communication paths that affect wake, scan, and reconnect timing.

---

## 2) Practical Power Path When Bud Goes Into the Case

Relevant implementation areas:
- apps/earphone/power_manage/app_chargestore.c
- cpu/br28/charge.c
- cpu/br28/power/power_app.c
- cpu/br28/power/power_check.c
- cpu/br28/power/power_port.c

Observed behavior in the current architecture:

1. Case/charge detect path notices insertion or lid/close state.
2. Chargestore management updates internal state.
3. A shutdown or soft-poweroff flow may be requested.
4. Bluetooth/TWS state is torn down or transitions into standby/listening states.
5. On removal from charger/case, the bud must wake its own local system, restore radio state, and then re-enter phone/TWS reconnect flow.

Important code anchors from chargestore path:
- `chargestore_check_going_to_poweroff()` checks if case-close shutdown is pending.
- `chargestore_shutdown_do()` can drive `power_set_soft_poweroff()`.

This means the user-visible delay is not just “Bluetooth is slow”. It is often a stacked delay:

1. physical removal detected
2. power-state transition exits
3. radio stack returns
4. TWS sibling search/reconnect starts
5. audio/call path becomes usable again

---

## 3) Why Removing a Bud from Charger Can Feel Slow

Even when TWS is fundamentally healthy, removal from charger/case may feel slow because several subsystems recover in sequence instead of all at once.

### 3.1 Power-state exit latency

The system must leave its charger/case-managed state first. If soft poweroff or a deep standby-like state was entered, wake is not instantaneous.

Contributors:
- retained RAM restore cost
- oscillator stabilization
- radio controller startup
- state-machine resumption in app layer

### 3.2 Bluetooth/TWS scan window timing

After wake, the bud does not immediately begin playing audio. It must first decide whether to:

1. reconnect phone
2. reconnect sibling
3. become discoverable/connectable

This handoff is managed by TWS reconnect logic rather than by pure hardware wake.

### 3.3 Charger/case policy overhead

If the case protocol still considers the bud in a transitional state, reconnect may start later than expected.

### 3.4 Audio service restart after link return

Even after the sibling link comes back, audio pipelines still need to refill and align before playback sounds stable.

---

## 4) Current Risks in the Power Strategy

### Risk A - Wake feels inconsistent

Root cause:
- wake time is the combined effect of power policy + charger state + reconnect state machine

User-visible symptom:
- sometimes bud reconnects quickly
- sometimes same action feels much slower

Why this happens:
- wake timing depends on the exact state at removal time, not only on hardware insertion/removal

### Risk B - One bud leaves the case earlier and gets ahead

Root cause:
- one bud may complete wake and reconnect path before the other exits its case/charge transition

User-visible symptom:
- one bud is already connected or already receiving audio while the other is still recovering

### Risk C - Case handling and reconnect handling are too tightly coupled

Root cause:
- charge/case workflow and TWS reconnect workflow are sequentially dependent

Impact:
- any delay in one layer becomes a delay in the whole user experience

### Risk D - Future tuning can easily disturb a working build

Root cause:
- low-power, charge, TWS scan, and role logic are strongly coupled

Impact:
- “small” optimization changes can create regressions in wake reliability, battery life, or case behavior

---

## 5) Safe Improvement Directions

These are documentation recommendations only, ordered from safest to riskiest.

### Improvement 1 - Measure before changing

Recommended first step:
- add timestamped UART logs around case removal, wake complete, sibling reconnect start, sibling reconnect success, phone reconnect success

Why:
- separates power delay from Bluetooth delay
- avoids guessing

### Improvement 2 - Tune reconnect policy before touching low-power policy

Safer than changing core power macros.

Examples:
- reduce dead time before sibling reconnect attempt
- verify page/inquiry scan windows after wake
- reduce reconnect path serialization where possible

Why safer:
- preserves the current stable power behavior while improving perceived responsiveness

### Improvement 3 - Review RAM retention size vs wake need

Current config:
- `TCFG_LOWPOWER_RAM_SIZE = 3`

Possible future study:
- determine whether this retention size is larger than necessary for the actual feature set

Potential benefit:
- lower wake overhead

Risk:
- wrong reduction can break feature resumption or internal state recovery

### Improvement 4 - Review generic low-power enable policy

Current config:
- `TCFG_LOWPOWER_LOWPOWER_SEL = 0`

This means the board is not using the general low-power entry in the usual way, but there are still case-driven and charge-driven transitions.

Future study:
- determine whether a cleaner distinction between “case standby” and “full reconnect-ready” state is needed

Risk:
- changing this without trace data can destabilize wake behavior

### Improvement 5 - Separate case-exit readiness from audio-start readiness

Best long-term UX direction:
- one milestone for “bud awake and link-ready”
- another for “audio buffers aligned and playback-ready”

Benefit:
- easier to understand where user-perceived lag comes from

Risk:
- requires broader architecture work, not a one-line config change

---

## 6) What Should Not Be Changed Blindly

Avoid changing these just to “make reconnect faster” without measurement:

- `TCFG_LOWPOWER_POWER_SEL`
- `TCFG_LOWPOWER_RAM_SIZE`
- charge enable / power-on policy macros
- case protocol enable decisions
- TWS reconnect search timing buried in runtime logic

Reason:
- these settings influence battery life, wake reliability, case behavior, and RF stability together

---

## 7) Recommended Documentation Outcome

For the current project, the correct statement is:

The reconnect delay seen after removing a bud from the charger is not only a TWS problem. It is a combined result of charge/case exit handling, power-state recovery, radio restart, sibling reconnect timing, and final audio pipeline refill.

So the first optimization target should be instrumentation and reconnect sequencing, not random changes to the low-power macros.

---

## 8) Related Files

- apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h
- apps/earphone/power_manage/app_chargestore.c
- cpu/br28/charge.c
- cpu/br28/power/power_app.c
- cpu/br28/power/power_check.c
- cpu/br28/power/power_port.c
- apps/earphone/bt_tws.c

---

## Related FIX Records

No fix records directly address the power subsystem. For planned power improvements, see [TODO-BACKLOG.md](../TODO-BACKLOG.md) (PM-001 — LDO vs DCDC).
