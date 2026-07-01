---
tags: [power, ldo, buck, dcdc, jl7016g, efficiency, battery]
date: 2026-04-28
board: JL7016G Hybrid
chip: AC701N (BR28)
status: Documentation only - no firmware code changes
---

# POWER PRIORITY 01 - LDO vs Buck DC-DC on JL7016G Hybrid

## Scope

This document is the first-priority power study for the current project.

Question being answered:

- if we want the next serious power improvement step, should we stay on LDO or move to Buck DC-DC?

This is not a code-change note. It is a decision document for the next power optimization phase.

---

## 1) Current confirmed project state

From the active board configuration:

- `TCFG_LOWPOWER_POWER_SEL = PWR_LDO15`
- `TCFG_LOWPOWER_LOWPOWER_SEL = 0`
- `TCFG_LOWPOWER_BTOSC_DISABLE = 0`
- `TCFG_LOWPOWER_RAM_SIZE = 3` in the current resolved feature path

Meaning:

- the board is currently running in LDO power mode
- the project is not yet using the more aggressive general low-power strategy
- the current build is tuned more for functional stability than for minimum battery current

Important current conclusion:

The first true hardware-level power optimization candidate is the system power mode itself, not only reconnect timing or small feature toggles.

---

## 2) What LDO and Buck DC-DC actually mean here

## 2.1 LDO mode

LDO means linear regulation.

Basic behavior:

- battery voltage is reduced to the internal rail by burning off the extra voltage as heat/current loss
- electrically simple
- usually cleaner and quieter from a noise perspective
- usually less efficient when battery voltage is much higher than the internal operating rail

In earbuds, LDO is often chosen first because:

- bring-up is easier
- analog audio paths are easier to stabilize
- less switching noise risk near microphone, DAC, ANC, touch, and RF domains

## 2.2 Buck DC-DC mode

Buck means a switching step-down converter.

Basic behavior:

- battery voltage is converted down more efficiently using switching energy transfer instead of dissipating the difference linearly
- can significantly reduce current draw in many active operating states
- introduces switching behavior, layout sensitivity, ripple, and possible EMI/noise coupling

In earbuds, buck is attractive because:

- battery is usually between about 4.2V full and ~3.xV in active use
- internal rails are much lower than the battery voltage
- wasting that voltage difference in LDO mode can cost real battery life

---

## 3) Why this matters more on JL7016G than on the old platform

From the provided datasheet evidence:

- JL7016G explicitly lists built-in LDO and Buck DC-DC converter support
- JL7016G package description includes dedicated buck-related pins such as `PGND` and `SW`
- AC6966B datasheet extract emphasizes built-in LDO rails and does not present the same buck path advantage in the same way

Practical meaning:

- JL7016G gives you a stronger hardware path for real power optimization than the older AC6966B datasheet baseline you provided
- so this is not just a firmware trick; this is one of the real hardware improvements available in the newer chip

---

## 4) Core efficiency comparison

At a high level:

### LDO efficiency idea

For linear regulation, rough efficiency behaves like:

$\eta_{LDO} \approx \frac{V_{out}}{V_{in}}$

Example intuition:

- if battery is 4.2V
- and the internal rail is around 1.25V to 3.0V depending on the domain
- LDO wastes the voltage difference as loss

That means LDO efficiency can become poor when:

- battery is near full
- load current is high
- many subsystems are active at once

### Buck efficiency idea

Buck efficiency is not that simple, but the important practical point is:

- a well-implemented buck can be much more efficient than an LDO for the same step-down task
- the bigger the voltage drop and the heavier the load, the more valuable buck usually becomes

So for active TWS earbuds running:

- Bluetooth radio
- ANC
- CVP/ENC
- audio DAC/ADC
- touch/in-ear logic

buck can provide meaningful battery-life improvement if the PCB and noise behavior are good.

---

## 5) Where LDO is stronger

LDO is still attractive in several ways.

### 5.1 Lower noise risk

LDO mode is usually safer for:

- DAC analog cleanliness
- microphone bias stability
- ANC analog sensitivity
- touch/reference stability
- reducing switching artifacts into RF or audio ground

### 5.2 Easier debug path

When the product is still stabilizing:

- LDO removes one big class of switching-ripple and power-integrity problems
- it shortens root-cause analysis when audio or wake behavior is already complex

### 5.3 Safer first-production choice

If the board layout or external buck support parts are uncertain:

- LDO is often the conservative working mode

This is likely part of why the current project stayed on `PWR_LDO15` while many other features were still being stabilized.

---

## 6) Where Buck DC-DC is stronger

### 6.1 Better battery efficiency in active states

Buck helps most when:

- battery voltage is high
- radio is active
- ANC/DSP load is active
- playback/call activity is continuous

This matches earbud real use surprisingly well.

### 6.2 Better path for long-session products

If the goal is:

- longer music playback
- longer call time
- less heat/waste at high load

buck is usually the first major architecture-level power lever.

### 6.3 Better value on JL7016G specifically

Since JL7016G explicitly exposes buck capability in the datasheet, this is one of the meaningful hardware improvements the newer chip gives you over the older platform.

---

## 7) Real risks of switching to Buck in this project

This is the part that matters most.

A buck-mode change is not a harmless config experiment.

### Risk A - Audio noise / hiss / spur coupling

Possible symptoms:

- background hiss increases
- ANC behavior worsens
- mic path becomes noisier
- DAC idle noise changes

Why:

- switching ripple can couple into analog rails, grounds, or bias nodes

### Risk B - RF behavior changes instead of improving

Possible symptoms:

- worse reconnect in some positions
- more packet loss near the head
- unstable behavior under low battery

Why:

- poor layout or insufficient filtering can let switching noise pollute sensitive RF conditions

### Risk C - Touch / in-ear sensitivity drift

Possible symptoms:

- false touches
- weaker reference stability
- in-ear threshold drift

Why:

- low-power capacitive sensing can react badly to supply noise if board design margin is weak

### Risk D - Wake/restart behavior changes

Possible symptoms:

- different wake timing
- new brownout-like issues during transitions
- charger/case behavior becomes less predictable

Why:

- once the core power mode changes, the whole system power integrity story changes with it

---

## 8) Hardware prerequisite check before any buck attempt

Before even considering firmware changes, verify the board hardware.

### Required checks

1. Are the JL7016G buck-related pins actually routed on the PCB?
2. Is the external inductor present and sized correctly?
3. Are the required output capacitors and grounding layout implemented correctly?
4. Is the analog ground / power partitioning good enough for audio + RF coexistence?
5. Was the board originally designed to support buck mode, or was it only pinned out incidentally?

Important point:

If the PCB does not correctly implement the buck external network, then switching from LDO to buck in firmware is not a valid optimization path.

In that case, the correct next power work is elsewhere.

---

## 9) Recommendation for this project

### 9.1 Strategic answer

Yes, LDO vs Buck DC-DC is the correct first-priority power comparison for this project.

Reason:

- it is the first architecture-level knob that can produce meaningful battery improvement on JL7016G
- it is one of the clearest hardware advantages JL7016G has over the older platform

### 9.2 Practical answer

But the next step is not:

- switch the macro blindly and hope for better battery life

The correct next step is:

1. verify PCB buck support
2. measure current in current LDO build
3. make one isolated buck experiment branch
4. validate audio/RF/touch before claiming any power win

---

## 10) Measurement plan for LDO vs Buck decision

Use the same board, battery condition, phone, codec, volume, and ANC state.

### Measure these scenarios in LDO mode first

1. case idle / soft-off behavior
2. out-of-case advertising idle
3. connected idle
4. music playback ANC off
5. music playback ANC on
6. call uplink/downlink active
7. reconnection after case removal

For each case, record:

- average current
- peak current
- wake/reconnect latency
- audio noise observations
- RF stability observations
- touch/in-ear stability observations

### Then repeat in Buck mode only if hardware supports it

Comparison result should decide:

- whether the battery gain is real
- whether the noise and stability tradeoff is acceptable

---

## 11) Decision matrix

| Decision factor                            | Stay on LDO | Move to Buck      |
| ------------------------------------------ | ----------- | ----------------- |
| Bring-up simplicity                        | Strong      | Weaker            |
| Analog noise safety                        | Stronger    | Riskier           |
| Active power efficiency                    | Weaker      | Stronger          |
| Battery-life improvement potential         | Lower       | Higher            |
| RF/layout sensitivity                      | Lower       | Higher            |
| Good first shipping mode                   | Yes         | Only if validated |
| Good first serious power optimization path | No          | Yes               |

---

## 12) Final conclusion

For this project, the correct first-priority power investigation is exactly this:

- compare the current `PWR_LDO15` path against a hardware-valid buck/DC-DC path

But the engineering conclusion is equally important:

- buck is the first major opportunity for battery improvement on JL7016G
- LDO is the safer baseline for stability
- the right next action is board-hardware verification and controlled A/B current testing, not an immediate production config switch

---

## 13) Related documents

- UPDATE/DOC LIBRARY/POWER DEEP DIVE — Charging Wake, Low Power, and Reconnect Latency.md
- UPDATE/DOC LIBRARY/BOARD — JL7016G Hybrid Config Deep Study.md
- UPDATE/MIGRATION COMPARISON/DATASHEET COMPARISON - AC6966B vs JL7016G (Hardware, BLE Antenna, Robustness).md
