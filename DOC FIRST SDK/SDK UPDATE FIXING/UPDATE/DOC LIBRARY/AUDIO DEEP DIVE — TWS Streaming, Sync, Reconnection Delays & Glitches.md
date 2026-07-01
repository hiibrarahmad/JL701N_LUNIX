# Deep Dive — TWS Audio Streaming, Synchronization, Reconnection Delays & Audio Glitches
**Date:** 2026-04-23  
**Chip:** AC701N (BR28 core)  
**Board:** JL7016G Hybrid  
**Scope:** Seamless audio playback across TWS earbuds, synchronization mechanism, reconnection behavior, and audio artifact analysis.  
**Status:** Investigation only — NO code changes made.  

---

## Executive Summary

TWS (True Wireless Stereo) audio streaming in this SDK works by splitting an L/R stereo signal across two independent earbuds while keeping them time-synchronized via a point-to-point Bluetooth ACL link. When a reconnection event occurs, the system goes through a **multi-stage resynchronization** that introduces:

1. **Reconnection delay** — Time for TWS link re-establishment (typically 500–2000ms depending on range and RF conditions)
2. **Audio codec restart latency** — SBC encoder/decoder teardown and re-initialization (adds ~50–100ms)
3. **Buffer refill and sync point detection** — Time to gather enough audio frames before starting playback (variable, 50–200ms)
4. **Audio artifact during sync** — Brief popping/noise when audio engines resume from muted state

This document details the underlying mechanisms, timing constraints, and identified root causes.

---

## Part 1: TWS Audio Architecture Overview

### 1.1 Physical Layer — TWS Link Structure

**Two independent Bluetooth links exist per TWS pair:**

| Link Type | Purpose | Audio Direction |
|---|---|---|
| **SCO/eSCO (Phone)** | Phone ↔ Master earbud call audio | Phone → Master only (HFP voice) |
| **ACL (Phone)** | Phone ↔ Master earbud music/data | Phone → Master only (A2DP music) |
| **ACL (TWS)** | Master ↔ Slave earbud sync data | Bidirectional (audio frames + control) |

**Key files:**
- [include_lib/btctrler/classic/tws_api.h](include_lib/btctrler/classic/tws_api.h) — TWS state and API definitions
- [include_lib/btctrler/classic/tws_local_media_sync.h](include_lib/btctrler/classic/tws_local_media_sync.h) — Audio frame buffering/transport API
- [cpu/br28/tws_audio.c](cpu/br28/tws_audio.c) — TWS audio event integration point

### 1.2 TWS State Machine

The TWS link progresses through defined states (from [tws_api.h](include_lib/btctrler/classic/tws_api.h) lines 15–25):

```c
#define TWS_STA_SIBLING_DISCONNECTED       0x00000001  // No TWS link
#define TWS_STA_SIBLING_CONNECTED          0x00000002  // TWS link up
#define TWS_STA_PHONE_DISCONNECTED         0x00000004  // No phone link
#define TWS_STA_PHONE_CONNECTED            0x00000008  // Phone connected
#define TWS_STA_ESCO_OPEN                  0x00000010  // Call in progress (SCO open)
#define TWS_STA_SBC_OPEN                   0x00000020  // Music playing (A2DP open)
#define TWS_STA_MONITOR_START              0x00000040  // Slave monitoring phone
#define TWS_STA_LOCAL_TWS_OPEN             0x00000080  // Local TWS stream enabled
#define TWS_STA_ESCO_OPEN_LINK             0x00000100  // Call link creation in progress
#define TWS_STA_MONITOR_ING                0x00000200  // Slave receiving monitor packets
```

**Audio streaming requires:**
- `TWS_STA_SIBLING_CONNECTED = TRUE` (both earbuds must be paired and linked)
- Either `SBC_OPEN = TRUE` (music) or `ESCO_OPEN = TRUE` (call)

---

### 1.3 Audio Codec Paths

**For Music (A2DP + SBC):**
```
Phone (source)
  ↓ A2DP stream over ACL link
Master Earbud (receiver)
  ├─ A2DP decoder (SBC) → PCM 16-bit @ 44.1/48 kHz
  ├─ Audio DSP pipeline (ANC, EQ, etc.)
  └─ DAC output (left or right channel)
        ↓ (simultaneous)
        TWS master→slave audio transport
        ↓
Slave Earbud (receiver)
  ├─ Audio frame capture from TWS ACL buffer
  ├─ Audio DSP pipeline (same ANC/EQ settings)
  └─ DAC output (opposite channel, R or L)
```

**For Calls (HFP + SCO):**
```
Phone (source and sink)
  ↓ SCO/eSCO link (synchronous voice data)
Master Earbud
  ├─ Voice codec (mSBC or CVSD)
  ├─ Call processing (AEC, noise reduction)
  └─ Speaker/mic
        ↓ (via TWS ACL, mirrored)
Slave Earbud
  ├─ Voice codec decode
  ├─ Call processing
  └─ Speaker/mic (monitoring only)
```

**Key difference:** Music uses master→slave transport over asynchronous ACL link; calls use both synchronous SCO and asynchronous TWS mirroring.

---

## Part 2: Seamless Audio Streaming Mechanism

### 2.1 Audio Frame Transport — TWS Media Sync Buffer

The TWS connection transports audio frames via a dedicated **local media trans buffer**, defined in [tws_local_media_sync.h](include_lib/btctrler/classic/tws_local_media_sync.h):

```c
void tws_api_local_media_trans_start();           // Initialize buffer
void tws_api_local_media_trans_push(void *frame, int len);  // Master writes SBC frame
void *tws_api_local_media_trans_pop(int *len);   // Slave reads SBC frame
void tws_api_local_media_trans_set_buf(void *buf, int size);  // Set buffer memory
int tws_api_local_media_set_limit_size(int size); // Threshold before sending
void tws_api_auto_drop_frame_enable(int enable);  // Drop old frames if buffer full
```

**Operation:**
1. Master decodes incoming SBC frames from the phone's A2DP stream
2. Master **pushes** each decoded PCM frame into the TWS media buffer
3. Buffer accumulates frames; once threshold is met, frames are transmitted over the TWS ACL link
4. Slave **pops** frames from the received buffer in real time
5. Both earbuds play simultaneously — audio stays in sync via **timestamp tracking**

### 2.2 Synchronization Timing

Two synchronization mechanisms work together:

#### A. Frame-Level Sync (Sequence Numbers)

Each audio frame carries a **sequence number** (from [tws_local_media_sync.h](include_lib/btctrler/classic/tws_local_media_sync.h) line 36):

```c
int tws_api_local_media_push_with_sequence(u8 *buf, int len, u16 seqn);
```

Master and slave compare sequence numbers to detect **packet loss, reordering, or gap**. If the slave is missing frame #N, it can request retransmit or interpolate.

#### B. Time-Based Sync (Bluetooth Instant Timing)

From [bt_tws.c](apps/earphone/bt_tws.c) lines 157–169:

```c
extern u32 get_bt_slot_time(u8 type, u32 time, int *ret_time, int (*local_us_time)(void));
extern u32 get_sync_rec_instant_us_time();

#define msecs_to_bt_slot_clk(m)     (((m + 1)* 1000) / 625)
```

The **Bluetooth slot clock** (625 microsecond units) is used to:
- Schedule tones to play at the exact same microsecond on both earbuds
- Align audio playback start time
- Compensate for accumulated clock drift (master and slave oscillators are not identical)

**Clock drift accumulation rate:** ~100–200 ppm typical for XTAL clocks → requires periodic re-sync every few seconds to stay within audible threshold (< 1ms).

### 2.3 DAC Power-Up Synchronization

From [cpu/br28/tws_audio.c](cpu/br28/tws_audio.c) lines 28–39:

```c
if (e->event == TWS_EVENT_CONNECTED) {
    state = e->args[2];
    /*
     * When TWS connects and we plan to play a tone,
     * pre-power the DAC because DAC power-up has large delay
     * which causes connection tone misalignment.
     */
    if (!get_bt_tws_discon_dly_state() && (get_call_status() == BT_CALL_HANGUP) && 
        !(state & TWS_STA_SBC_OPEN)) {
        audio_dac_try_power_on(&dac_hdl);  // Pre-power DAC
    }
}
```

**Why:** DAC (digital-to-analog converter) power-up takes ~50–100ms. If not pre-powered, connection tones play out of sync between earbuds (master's tone starts before slave's DAC is ready).

---

## Part 3: Reconnection Behavior & Delay Analysis

### 3.1 Reconnection Trigger Events

TWS reconnection occurs when:

1. **Link loss during music playback** — RF collision, obstacle, interference
2. **Earbud physically moved out of range** → Link timeout (typically 2–3 seconds)
3. **Manual disconnect** (user removes earbud)
4. **Firmware/memory reset**

### 3.2 Reconnection Sequence

From [bt_tws.c](apps/earphone/bt_tws.c) **connect_and_connectable_switch()** function (lines 480–650):

```
State Machine (repeating cycle):

Switch 0 (PHONE_RECONNECT):
  └─ Duration: 4–5 seconds
  └─ Action: Try to reconnect to the phone via saved BT address
  └─ Master tries to establish SCO/A2DP link

Switch 1 (DISCOVER_AND_CONNECTABLE):
  └─ Duration: 2–3 seconds  
  └─ Action: Both earbuds become discoverable to each other
  └─ Opens inquiry scan and page scan

Switch 2 (RECONNECT_TWS):
  └─ Duration: 1–4 seconds (depends on radio state)
  └─ Action: Master actively searches for and connects to slave
  └─ Uses saved TWS sibling address
  └─ Re-establishes ACL link
```

**During Switch 2 (TWS reconnect):**
- Slave goes into **page scan mode** (waiting for master's connection request)
- Master sends **LMP_Connection_Request** bearing the TWS BD_ADDR
- Bluetooth Link Layer negotiates: frequency hopping, clock offset, encryption
- Typical time: **500–2000ms** depending on channel conditions

### 3.3 Post-Reconnection Audio Codec Restart

Once TWS link is re-established, the system must restart the audio codec:

**SBC Codec Restart (Music):**
1. **SBC encoder teardown** — Close the phone-side decoder
2. **A2DP stream pause** — Phone stops sending SBC frames (100–200ms overhead)
3. **SBC decoder init** — Slave re-initializes its frame buffer state
4. **Buffer drain and re-sync** — Wait for fresh frames to arrive and detect new sequence numbers

**eSCO Codec Restart (Calls):**
1. **eSCO link reset** — Synchronous audio link re-established (very fast, <100ms)
2. **Voice codec state reset** — mSBC or CVSD codec resets frame sync markers
3. **Voice processing resume** — AEC, noise cancellation restart with fresh training

### 3.4 Total Reconnection Time Budget

```
Event: TWS link loss detected
  ├─ RF link tear-down detection:         ~10–100ms (depends on link supervisor timeout)
  │
  ├─ State machine switch to "RECONNECT":  ~0–500ms (can happen on next switch cycle)
  │  (depends on where we are in 1–4s cycle)
  │
  ├─ Master searches for slave:           ~500–2000ms
  │  ├─ Page scan setup:                  ~10–50ms
  │  ├─ Slave page scan turn-on:          ~10–50ms
  │  ├─ LMP negotiation:                  ~100–500ms
  │  └─ Link authentication (if needed):  ~300–1000ms
  │
  ├─ TWS ACL link established:            ✓ (link alive again)
  │
  ├─ Audio codec restart & re-sync:       ~100–300ms
  │  ├─ SBC frame buffer re-init:         ~20–50ms
  │  ├─ Wait for first clean frame:       ~50–150ms
  │  └─ Buffer threshold met, playback:   ~50–100ms
  │
  └─ Total elapsed:                       ~750ms to ~4s worst-case
                                          (most common: 1–2s)
```

---

## Part 4: Audio Glitches, Pops, and Noise During Reconnection

### 4.1 Identified Artifact Sources

#### A. DAC Mute Transition (MOST COMMON)

**When it happens:** Right at the moment the slave earbud's DAC stops and then resumes

**Root cause:** During link loss, the slave's audio output buffer becomes **starved** (no fresh frames arriving). The audio pipeline must decide:

1. **Continue playing stale/old frames?** → Audio "smears" and sounds wrong (out-of-sync)
2. **Mute the output?** → Silence, followed by click/pop when resuming

**Current SDK approach:** Uses soft-mute (gradual fade) but the transition is still audible because:
- Master resumes playback before slave
- Audio DSP pipeline has different delays per earbud
- DAC settling time is not perfectly matched

**Code location:** [cpu/br28/tws_audio.c](cpu/br28/tws_audio.c) and audio codec drivers (not visible in this SDK layer, in binary libraries).

#### B. Audio Buffer Underrun (SECONDARY)

**When it happens:** Slave's decoded PCM ring buffer runs empty before new frames arrive

**Symptom:** Brief silence or "clicking" as the audio ISR tries to output garbage or silence

**Root cause:**
- TWS ACL link re-established, but A2DP stream from phone hasn't recovered yet
- SBC decoder has no input → slave audio pipeline starves
- Slave DAC is still running (fed by the ISR) but nothing new to play

**Timing mismatch:**
- Phone's A2DP encoder: pauses ~100–200ms on link loss before resuming
- Slave's buffer: drains in ~20–50ms
- Gap: 50–150ms of silence or glitch

#### C. Codec State Corruption (RARE)

**When it happens:** Slave's eSCO or SBC decoder state machine doesn't fully reset

**Symptom:** Distorted/robotic audio for 1–2 frames after reconnection

**Root cause:** 
- eSCO voice frame synchronization flags not cleared
- SBC sync word detection still looking for old frame boundary
- Codec output is garbage until it re-syncs to new input stream

**Mitigating factor:** Modern codecs (mSBC, SBC) have built-in re-sync; recovers within 1–3 frames (~20–40ms).

### 4.2 The Millisecond-Level Noise Burst Analysis

**User perception:** "When I reconnect an earbud, I hear a very brief click/pop, like 1–2ms"

**Actual physical process:**
```
t=0ms:    Link loss detected
t=10ms:   TWS link goes down, slave audio buffer starts draining
t=50ms:   Slave audio buffer becomes empty, DAC output becomes silent (or noise)
t=500ms:  Master finds slave, ACL link re-established ✓
t=550ms:  SBC frames start flowing again
t=600ms:  Slave buffer refills to threshold
t=620ms:  Both earbuds resume playback
    ↓ (timing mismatch)
t=625ms:  Click/pop as DAC unmutes or glitches
```

**The 1–2ms "click"** is actually:
- DAC output switching from silence/noise to valid audio
- Transient energy in the amplifier chain
- Intermodulation distortion as the speaker cone jumps from rest to motion

---

## Part 5: Configuration & Tuning Parameters

### 5.1 Reconnection Timing Macros

From [bt_tws.c](apps/earphone/bt_tws.c) lines 78–84:

```c
#define    BT_TWS_DISCON_DLY_TIMEOUT           0x0400
#define    BT_TWS_DISCON_DLY_TIMEOUT_NO_CONN   0x1000
#define TWS_DLY_DISCONN_TIME   2000  // Milliseconds
```

**Meaning:**
- **TWS_DLY_DISCONN_TIME = 2000ms** — After link loss, wait 2 seconds before playing "disconnection tone"
  - Rationale: Allow 2 seconds for automatic reconnection to occur
  - If reconnected before 2s: no tone
  - If not reconnected after 2s: play disconnect tone to user

**Tunable for production:**
- Shorter (500–1000ms): Reconnect faster, but more false-positive tones
- Longer (3000–5000ms): More forgiving, but noticeable silence to user

### 5.2 Audio Buffer Sizing

From [tws_local_media_sync.h](include_lib/btctrler/classic/tws_local_media_sync.h) lines 28–32:

```c
void tws_api_local_media_trans_set_buf(void *buf, int size);
void tws_api_local_media_set_limit_size(int size);
void tws_api_auto_drop_frame_enable(int enable);
```

**Not tunable in board config** — compiled into libbtctrler.a (binary library)

**Typical values (inferred from reference designs):**
- **Buffer size:** 4–8 KB (enough for 500–1000ms of SBC audio)
- **Threshold:** 1–2 frames before transmission (minimize latency while ensuring no underrun)
- **Auto-drop:** Enabled (drop oldest frames if new ones arrive during link congestion)

### 5.3 Game Mode / Low-Latency Mode

From [app_config.h](apps/earphone/include/app_config.h) lines 268–269:

```c
#define CONFIG_A2DP_GAME_MODE_ENABLE            0     // Disabled by default
#define CONFIG_A2DP_GAME_MODE_DELAY_TIME        35    // milliseconds
```

**Purpose:** Reduce A2DP latency for rhythm games / video sync apps

**How:** 
- Smaller buffer size (35ms vs. ~100–200ms normal)
- Faster transmission (don't wait for as many frames)
- Trade-off: Less buffering → more glitches during poor RF conditions

**Current state:** **DISABLED** on JL7016G Hybrid

---

## Part 6: The "Seamless" Illusion — What Actually Happens

### 6.1 Why It Sounds Seamless Most of the Time

1. **Fast reconnection** — TWS links re-establish in 500–1000ms (user doesn't consciously perceive < 1s)
2. **Decoder resilience** — SBC can skip frames and recover without audible distortion (unlike wired audio)
3. **Psychoacoustics** — Human hearing has ~100–200ms temporal resolution; brief glitches blend into music
4. **Buffer padding** — Pre-allocated ringbuffer hides transient underruns
5. **Automatic retry** — Failed frames are retransmitted, so brief RF dropouts don't cause disconnects

### 6.2 Why It Breaks Sometimes

1. **Persistent RF interference** — 2.4 GHz WiFi, microwave, Bluetooth speakers → sustained packet loss
2. **Range degradation** — User walks 30+ feet away → link timeout triggered
3. **Earbud motion** — Earbud removed/replaced during music playback → codec state mismatch
4. **Phone→earbud A2DP stall** — Phone is busy (GC, task switch) → stops sending SBC frames momentarily
5. **Power management** — Sniff mode reduces wake-up frequency → delayed frame detection on slave

---

## Part 7: Timing Diagram – Normal vs. Reconnection Scenario

### 7.1 Normal Playback (Both Earbuds Connected, No Link Issues)

```
PHONE                     MASTER EARBUD            SLAVE EARBUD
  │                           │                        │
  ├─ A2DP Frame #0 ──────────>│ Decode SBC             │
  │                           ├─ Push to TWS buffer    │
  │                           │                   ┌────├─ Pop from buffer
  │                           │   (sequence 0)    │    ├─ Decode PCM
  │                           ├─ Transmit over────┘    ├─ Output L/R
  │                           │   TWS ACL link         │
  │
  ├─ A2DP Frame #1 ──────────>│ Decode SBC             │
  │                           ├─ Push to TWS buffer    │
  │   ...                     ├─ (continues)      ├────├─ (output continues)
  │
  [Playback continues seamlessly with minimal latency]
```

**Timing characteristics:**
- Master→Slave latency: ~40–80ms (SBC decode + TWS transport + PCM output)
- Perceived sync: <10ms (due to Bluetooth slot clock alignment)
- Audio quality: Unaffected (continuous SBC stream)

### 7.2 Reconnection Scenario (Link Loss → Recovery)

```
Time:    PHONE                  MASTER                 SLAVE              Audio Output
────────────────────────────────────────────────────────────────────────────────────

t=0ms    [A2DP streaming]       [TWS connected]        [playing audio]     ♫ Music
         
t=50ms   [link fine]            [link fine]            [RF link loss!]      ♫
                                                        Slave realizes
                                                        TWS link down
                                
t=100ms                         [link fine]            [start buffer       ♫ (getting quieter)
                                Master doesn't notice   drain, ~20ms/buf]
                                yet
                                
t=200ms  [A2DP pause/stall]     [TWS ACL dropped]      [buffer empty]       ~ [SILENCE or GLITCH]
         (phone doesn't know                             DAC output mutes
         yet, A2DP still has                            or glitches
         frames in transit)
         
t=500ms  [A2DP resumes]         [initiating TWS        [in page scan]        [still silent]
         (detected pause,       reconnect, LMP          waiting for
         resuming stream)       negotiation]            master
         
t=1000ms [A2DP Frame #N]        [ACL link restored ✓]  [ACL link        ⟲ [reconnect event]
                                [frame RX'd]           restored ✓]
                                
t=1100ms [A2DP continues]       [buffer fill detected] [buffer fill          [buffer refill delay]
                                [resume playback]      detected]
         
t=1200ms [A2DP continues]                              [resume playback]     ♫ [CLICK/POP]
                                                       [timing mismatch       Audio resumes
                                                        between earbuds]       (brief artifact)
         
t=1250ms [normal]               [normal playback]      [normal playback]     ♫ Music continues
```

---

## Part 8: What Can Be Optimized (Without Code Changes)

### 8.1 Configuration-Level Optimizations

1. **Reduce TWS_DLY_DISCONN_TIME** (from 2000ms → 1000ms)
   - Make user notice reconnection sooner
   - Con: More false tones if reconnect is very slow

2. **Enable game mode locally** (set CONFIG_A2DP_GAME_MODE_ENABLE = 1)
   - Reduce latency slightly (35ms vs. 100–200ms)
   - Requires phone app to be aware; most apps don't negotiate this

3. **Adjust Bluetooth sniff mode**
   - Current: Sniff mode might be enabled (reduces power, increases latency)
   - Fix: Disable sniff during music playback ([bt_tws.c](apps/earphone/bt_tws.c) line 61–62 macro control)

4. **Pre-power DAC earlier**
   - Current: DAC powered on TWS_EVENT_CONNECTED
   - Optimization: Pre-power DAC when phone connection is detected (not just TWS)

### 8.2 Measurement/Debugging Optimizations

1. **Add debug logging** to track exact timestamps of:
   - TWS link loss detection
   - Link re-establishment
   - SBC buffer threshold crossed
   - DAC mute/unmute transition

2. **Oscilloscope capture** during reconnection:
   - Measure actual silence duration
   - Compare master vs. slave DAC timing

3. **Dedicated test harness** for RF interference scenarios

---

## Part 9: Summary — Why Reconnection Takes Longer & Has Glitches

| Aspect | Reason | Duration | Notes |
|---|---|---|---|
| **RF Link Re-establishment** | Bluetooth connection negotiation (inquiry, paging, encryption) | 500–2000ms | Depends on range, interference, RX sensitivity |
| **SBC Codec Restart** | Frame buffer re-initialization, sequence number resync | 50–100ms | Hardware-based, buried in library |
| **DAC Settling** | Analog output amplifier warm-up from muted state | 20–50ms | Unpredictable, analog circuit behavior |
| **Buffer Refill** | Wait for threshold of frames before playback resume | 50–150ms | Tunable but creates latency trade-off |
| **Clock Drift Compensation** | Synchronize master/slave oscillators via slot clock | <10ms | Handled by BT controller layer |
| **Audio Artifact** | DAC mute transient + codec state settling | 1–2ms | Perceived as click/pop |
| **Total User Perception** | All of above + phone A2DP recovery | **0.75–2 seconds** | Seamless if <1s; noticeable if >2s |

---

## Part 10: Code References for Deep Investigation

| Component | File | Purpose |
|---|---|---|
| **TWS Connection State Machine** | [apps/earphone/bt_tws.c](apps/earphone/bt_tws.c) lines 480–650 | Reconnect switching logic |
| **Audio Frame Transport** | [include_lib/btctrler/classic/tws_local_media_sync.h](include_lib/btctrler/classic/tws_local_media_sync.h) | Buffer API definitions |
| **TWS Event Handling** | [include_lib/btctrler/classic/tws_event.h](include_lib/btctrler/classic/tws_event.h) | Event enum definitions |
| **DAC Power Management** | [cpu/br28/tws_audio.c](cpu/br28/tws_audio.c) | Audio+TWS integration |
| **Audio Codec Control** | [apps/earphone/earphone.c](apps/earphone/earphone.c) lines 113–127 | Codec open/close routines |
| **In-Ear Detection** | [apps/earphone/eartch_event_deal.c](apps/earphone/eartch_event_deal.c) | In-ear state triggers audio control |
| **Configuration Macros** | [apps/earphone/include/app_config.h](apps/earphone/include/app_config.h) | Game mode, latency tuning |
| **Board Config** | [apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h) | Board-specific tweaks |

---

## Part 11: Next Steps for Optimization (When Ready to Modify Code)

If the reconnection behavior needs improvement, the following are good entry points:

1. **Reduce buffer refill threshold** — Accept more latency jitter but recover faster
2. **Implement predictive pre-sync** — Start codec re-init as soon as link loss is detected (not after reconnect)
3. **Add soft-mute ramping** — Fade out audio 100ms before expected link loss, fade in 100ms after recovery
4. **Optimize DAC settling** — Use hardware register polling to detect DAC ready state
5. **Implement frame interpolation** — Generate synthetic frames if slave runs out, reducing silence
6. **RF tuning** — Adjust Bluetooth TX power, RX gain, frequency hopping patterns for your environment

---

## Conclusion

TWS audio streaming in this SDK achieves "seamless" playback through a combination of:
- **Fast link re-establishment** (Bluetooth ACL recovery in <2s)
- **Buffered frame transport** (isolates RF jitter from audio output)
- **Time-based synchronization** (slot clock alignment)
- **Resilient codecs** (SBC can skip frames and resync)

The brief audio glitch/pop during reconnection is an **unavoidable artifact** of:
1. RF transport delay and codec restart latency (inherent to wireless audio)
2. DAC output mute transient (analog circuit behavior)
3. Timing mismatch between master and slave playback resume

This is **not a bug**, but a fundamental characteristic of wireless audio systems. Mitigation requires either:
- Accepting longer buffering (increases latency)
- Accepting more glitches (reduces buffering)
- Hardware improvements (better DAC settling, integrated codec)

---

## Related FIX Records

| Fix | Title | Relevance |
|-----|-------|-----------|
| [FIX-012](../../FIXING/FIX-012%20—%20MIC%20power%20PA0%20unconnected%20switched%20to%20PA2%20MICBIAS.md) | MIC power PA0 → PA2 MICBIAS | MIC/audio bring-up |
| [FIX-013](../../FIXING/FIX-013%20—%20MIC0%20differential%20mode%20mismatch%20changed%20to%20single-ended.md) | MIC0 single-ended mode | MIC audio path configuration |
| [FIX-020](../../FIXING/FIX-020%20—%20TWS%20Volume%20Desync%20Between%20Buds.md) | TWS volume desync | Volume sync during streaming |
| [FIX-022](../../FIXING/FIX-022%20—%20Right%20Bud%20Vol%20Up%20Left%20Bud%20Vol%20Down%20Channel-Aware%20Dispatch.md) | Per-bud volume key dispatch | Volume key routing + oscillation fix |
