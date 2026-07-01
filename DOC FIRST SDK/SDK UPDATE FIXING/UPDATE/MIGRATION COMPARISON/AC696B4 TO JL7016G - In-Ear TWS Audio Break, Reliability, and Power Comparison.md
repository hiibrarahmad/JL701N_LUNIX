---
tags: [migration, ac696b4, jl7016g, tws, in-ear, power, reliability]
date: 2026-04-27
board: JL7016G Hybrid
chip: AC701N (BR28)
status: Documentation only - no firmware code changes
---

# AC696B4 to JL7016G Migration - In-Ear TWS Audio Break, Reliability, and Power Comparison

## 0) Why this document exists

You migrated from AC696B4 to JL7016G and previously faced a critical user issue:

- when bud entered ear / in-ear logic triggered, TWS became unstable
- audio did not reliably continue through both earbuds
- user-perceived result: TWS felt broken after wear-state change

This note answers:

1. Will it work now on JL7016G with your current project state?
2. Why the failure happened before (root-cause map).
3. How much improvement is expected on JL7016G versus AC696B4.
4. Power-consumption comparison with the highest accuracy possible from available project evidence.

Important constraint:

- This workspace contains detailed JL7016G implementation evidence, but no complete AC696B4 project + board configs + measurement logs.
- So this comparison uses evidence tiers:
  - Tier A (Verified): directly confirmed in your current JL7016G code/docs.
  - Tier B (High confidence): architecture-level behavior common to these SDK lines.
  - Tier C (Needs lab data): requires current/latency measurements for numeric certainty.

---

## 1) Direct answer first

### 1.1 Will this work now?

Short answer: Yes, it is much more likely to work correctly now on your JL7016G project, because the exact classes of routing/filtering issues that can break in-ear + TWS user behavior were identified and fixed in this codebase.

But not a blind 100% guarantee.

What is still required for production-level confidence:

- run the validation matrix in Section 9 on real hardware
- include out-of-case and in-case transitions
- include weak RF and low battery scenarios

### 1.2 Is JL7016G improved compared with AC696B4 for this use case?

Yes, in practical project terms, improvement is significant for your use case because:

- your current JL7016G branch already contains targeted fixes in touch/in-ear event routing, TWS identity persistence handling, and reconnect understanding
- your documentation and tracker now provide controlled behavior instead of unknown historical behavior

However, exact percentage improvement cannot be truthfully stated without A/B measurement from both platforms under identical firmware policy and hardware conditions.

---

## 2) Symptom-to-system map for your old AC696B4 issue

Old symptom:

- inserting bud in ear caused TWS/audio path instability (or apparent break)

In this SDK family, this kind of symptom is usually not one single bug. It is a chain interaction:

1. in-ear state transition or reference-channel behavior changes key/event pipeline
2. event remap/filtering can suppress or alter control events
3. TWS sibling state and reconnect timing can diverge between buds
4. audio buffer realignment lags after link recovery
5. user hears one side first, delayed side second, or temporary mute/desync

So the problem often appears as "TWS broke" while the real fault may be event gating + reconnect sequencing + audio refill timing.

---

## 3) What is verified in your JL7016G project today (Tier A)

The following is already present in your current workspace and is directly relevant to the old symptom class.

### 3.1 In-ear / touch routing hardening is already done

Verified from your documented fixes and board behavior:

- PB4 gesture route/drop chain fixed
- long/hold suppression gate fixed
- reference-channel-related event loss path fixed
- in-ear remap hook guarded to avoid filtering when ear-detect is disabled

Why this matters to your old issue:

- these are exactly the points that can make wear-state transitions feel like TWS/audio failure to users

### 3.2 TWS identity model is persistent and explicit

Verified from current TWS deep-dive evidence:

- sibling/local/common addresses are persisted
- reconnect is not always fresh random discovery
- charge/case flow can reinforce stored sibling identity behavior

Why this matters:

- stable sibling identity reduces random or cross-pair behavior during wake/reconnect

### 3.3 Power/reconnect interaction is understood in current docs

Verified from current power deep-dive:

- reconnect delay is multi-stage (case exit, wake, radio, sibling reconnect, buffer refill)
- this prevents wrong debugging assumptions and supports targeted tuning

Why this matters:

- it reduces false fixes that may break stability while trying to speed reconnect

### 3.4 Audio top-level volume behavior is now controlled intentionally

Verified from tracker/document updates:

- JL7016G ANC digital ceiling lifted from -17 dB to -6 dB for this board path

Why this matters:

- avoids interpreting low loudness as missing channel/output failure in edge tests

---

## 4) Why your old "in-ear triggers TWS break" could happen on previous platform

The most likely mechanisms (Tier B) are:

1. Event remap/filtering conflict:
   - in-ear detect control key path can remap/drop key events if state assumptions are wrong

2. Reference channel coupling side effects:
   - if touch reference channel is also part of user-control behavior, transitions can create invalid/ignored events

3. TWS reconnect race:
   - one bud exits case/power-state earlier and resumes link/audio faster than sibling

4. Audio pipeline alignment lag:
   - TWS link appears connected before both audio paths are truly synchronized

5. Stale identity persistence:
   - old/stale sibling address records can cause reconnect anomalies that look like random breakage

None of these requires bad hardware to happen. They are state-machine and policy interactions.

---

## 5) AC696B4 vs JL7016G comparison table (accuracy-scored)

Scoring legend:

- Evidence: A = verified in current project, B = high confidence, C = measurement needed
- Impact scale: Low / Medium / High

| Dimension | AC696B4 (historical from your report) | JL7016G current project | Expected improvement | Evidence |
|---|---|---|---|---|
| In-ear transition robustness | Reported break-like behavior on wear transition | Multiple in-ear/touch routing fixes already integrated | High | A/B |
| PB4/reference channel stability | Likely conflict-prone in old flow | Explicit reference handling and routing hardening documented | High | A |
| TWS sibling identity consistency | Could be affected by stale pair context | Persistent local/remote/common address model explicitly documented and used | Medium to High | A |
| Reconnect determinism after case exit | User observed unstable result | Multi-stage reconnect path understood and now documented for targeted tuning | Medium | A/B |
| Audio resume synchronization | Could appear broken due to delayed side | Known as buffer/refill/sync milestone issue, no longer treated as mystery | Medium | A/B |
| Debuggability | Likely lower due to less structured investigation history | Rich tracker + deep dives + known anchors | High | A |
| Loudness margin under ANC path | Could be interpreted as weak output | Top digital ceiling adjusted to board-safe limit | Medium | A |

Interpretation:

- For your exact historical failure mode, JL7016G project state is materially better prepared and likely more stable.
- Most of the gain comes from integration maturity and bug fixes, not only from chip label change.

---

## 6) Power consumption comparison (most accurate possible from current evidence)

### 6.1 What can be said with confidence right now

From your JL7016G board config and power deep-dive:

- power mode is LDO path (`PWR_LDO15`), not the most aggressive efficiency mode
- generic low-power entry is disabled in current board config (`TCFG_LOWPOWER_LOWPOWER_SEL = 0`)
- RAM retention footprint is high (`TCFG_LOWPOWER_RAM_SIZE = 3`)
- ANC path is enabled in this project, which increases system power in active listening modes

Therefore:

- your current JL7016G build is optimized for functional stability and feature behavior, not minimum battery draw

### 6.2 Fair comparison logic: chip potential vs product configuration

Power comparison has two layers:

1. Silicon/platform potential (IC capability)
2. Actual product policy (your config, features, wake/reconnect strategy)

In real products, layer 2 can dominate.

That means:

- A newer IC can still consume equal or more power than an older one if feature load and power policy are heavier.

### 6.3 Practical expectation for your current migration

Given current JL7016G config:

- Idle/case/wake behavior: likely improved behavior stability, not guaranteed lower current yet
- Active music with ANC: may be same or higher current than a lighter AC696B4 configuration
- Call + TWS + ANC/cvp-heavy paths: power can be noticeably higher if all blocks run continuously

So the accurate statement is:

- Reliability and controllability improved strongly.
- Power efficiency improvement is not guaranteed yet in this exact build; it requires targeted low-power optimization work.

### 6.4 Estimated directional table (not a measured mA claim)

| Scenario | Expected JL7016G vs older AC696B4 setup | Confidence |
|---|---|---|
| Deep standby / case-off-like state | Similar to better, depending on final low-power policy | Medium |
| Connected idle (no audio) | Similar to slightly better if scan/reconnect policy is tuned | Medium-Low |
| Music playback ANC off | Similar to better possible with optimized clocks/path | Medium-Low |
| Music playback ANC on | Similar to higher in current config due to active ANC chain | Medium |
| Call + TWS + DSP-heavy pipeline | Similar to higher unless profile is tuned | Medium |

---

## 7) "How much improved" - best honest quantification

Without dual-platform lab logs, numeric percentage would be guesswork.

Best accurate quantification today:

- Functional reliability improvement for your reported in-ear/TWS-break symptom class: High.
- Power improvement certainty: Low to Medium until measured.

If you want true numeric comparison, run the test plan in Section 8 and report:

- current (mA) profile in each scenario
- wake-to-audio latency (ms)
- reconnect success rate (%) after repeated case cycles

---

## 8) Measurement plan for truly accurate AC696B4 vs JL7016G comparison

Use same battery, same speaker load, same RF environment, same volume, same codec, same phone.

### 8.1 Power measurements

Collect average and peak current for:

1. case inserted (sleep path)
2. out-of-case idle advertising
3. connected idle
4. music playback ANC off
5. music playback ANC on
6. call uplink/downlink active

Minimum repeats per test: 10 cycles.

### 8.2 Latency and reliability measurements

Collect:

1. bud removal to BT connected (ms)
2. bud removal to stable audio on both sides (ms)
3. side mismatch duration when mismatch occurs (ms)
4. fail/retry rate over 100 case cycles

### 8.3 Pass criteria recommendation

- TWS/audio break after in-ear transition: 0/100 allowed
- one-side-only audio longer than 500 ms after reconnect: < 2/100 events
- reconnect success after case removal within target window: > 98%

---

## 9) Validation matrix for your current JL7016G build

Run all rows on real hardware:

1. single bud wear/unwear cycles x50
2. both buds wear/unwear asynchronous x50
3. case open/close fast cycle x50
4. low battery (<20%) wear/unwear x30
5. weak RF edge (phone 8-10m + obstacles) x30
6. phone call ongoing while wear state changes x30
7. ANC on/off transitions during reconnect x30

Log each run as:

- pass/fail
- left/right audio presence timeline
- reconnect time
- any key-event mismatch

---

## 10) Final recommendation

For your specific concern:

- moving from AC696B4 to the current JL7016G project is the correct direction and is likely to solve the previous in-ear-triggered TWS/audio-break behavior in practice, because the exact failure classes have already been addressed in this branch.

For power:

- do not assume automatic battery gain from IC migration alone.
- your current JL7016G settings prioritize stability and feature completeness.
- run Section 8 measurements, then tune low-power/reconnect policy carefully to convert platform potential into real battery improvement.

---

## 11) Related existing documentation in this project

- UPDATE/DOC LIBRARY/TWS DEEP DIVE - Reconnect Lag, Bud Identity, MAC Strategy, and Risks.md
- UPDATE/DOC LIBRARY/POWER DEEP DIVE - Charging Wake, Low Power, and Reconnect Latency.md
- UPDATE/DOC LIBRARY/IN-EAR DETECTION - CTMU Capacitive Sensing, GPIO Mapping, State Machine.md
- UPDATE/DOC LIBRARY/00 - SDK Progress Tracker.md
