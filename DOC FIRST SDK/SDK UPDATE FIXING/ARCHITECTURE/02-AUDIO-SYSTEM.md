---
tags: [architecture, audio, codec, streaming, tws]
date: 2026-05-01
---

# 🔊 Audio Processing Architecture

**Purpose:** Understand audio signal flow from input to output and TWS streaming.

---

## Audio Signal Flow

```
Microphone Input (CTMU/ADC)
        ↓
Audio Codec (ADC)
        ↓
Audio Effects Processing
    ├─ ANC (Noise Cancellation)
    ├─ EQ (Equalization)
    ├─ Dynamic Range
    └─ Format Conversion
        ↓
Bluetooth Encoder
    ├─ Codec Selection (AAC, SBC, LDAC, aptX, OPUS)
    └─ Bitrate Setting
        ↓
TX to Remote Earphone (TWS)
        ↓
RX from Remote (If in other bud)
        ↓
Bluetooth Decoder
        ↓
Audio Effects (Same pipeline)
        ↓
Audio Codec (DAC)
        ↓
Speaker Output
```

---

## Supported Codecs

| Codec | Bitrate | Quality | Use Case |
|-------|---------|---------|----------|
| **SBC** | 128-320 kbps | Standard | Baseline, all devices |
| **AAC** | 96-256 kbps | Good | Mobile compatibility |
| **LDAC** | 330-990 kbps | Premium | High-quality audio |
| **aptX** | 352 kbps | Excellent | Low latency |
| **OPUS** | 64-510 kbps | Dynamic | Voice calls |

---

## Audio Configuration

### Board Level Settings
```c
// In board_jl7016g_hybrid_cfg.h:
#define TCFG_AUDIO_CODEC_ENABLE          1
#define TCFG_AUDIO_EFFECT_ENABLE         1
#define TCFG_ANC_ENABLE                  1
#define TCFG_IQ_AUDIO_ENABLE             0  // IQ reconstruction
```

### Codec Selection
```c
// Set via GUI DOCUMENTATION TAB 01:
Bluetooth Codec: [Select from supported]
Bitrate: [Choose quality level]
Sample Rate: 16 kHz / 48 kHz
```

---

## TWS Audio Synchronization

**Challenge:** Keep both earphones synchronized during audio playback

**Solution:**
```
Master Bud:
    Receives audio from phone
    ↓
    Processes & Encodes
    ↓
    Sends to Slave via Bluetooth
    ↓
    Outputs with timing reference

Slave Bud:
    Receives encoded audio
    ↓
    Decodes & Processes
    ↓
    Synchronizes to Master timing
    ↓
    Outputs synchronized audio
```

**Sync Accuracy:** < 50 ms latency (imperceptible to human ear)

---

## ANC (Active Noise Cancellation)

**Purpose:** Reduce ambient noise in incoming audio

**Mechanism:**
```
Ambient Sound (Mic Input)
        ↓
FFT Analysis
        ↓
Frequency Decomposition
        ↓
Inverse Phase Generation
        ↓
Mix with Speaker Output
        ↓
Net: Cancellation of ambient noise
```

**Configuration Levels:**
- OFF: No cancellation
- LOW: Gentle cancellation
- MEDIUM: Balanced
- HIGH: Aggressive cancellation

---

## Latency Targets

| Stage | Target | Typical |
|-------|--------|---------|
| Mic to Input Buffer | < 5 ms | 3-4 ms |
| Audio Processing | < 20 ms | 10-15 ms |
| Codec Encoding | < 30 ms | 15-25 ms |
| Bluetooth TX | < 50 ms | 20-40 ms |
| Decoding | < 30 ms | 15-25 ms |
| DAC Output | < 10 ms | 5-8 ms |
| **Total** | **< 145 ms** | **70-115 ms** |

---

**Related Documentation:**
- [→ AUDIO CODEC QUALITY](../UPDATE/DOC%20LIBRARY/AUDIO%20CODEC%20QUALITY%20—%20Supported%20Codecs,%20Bitrates%20&%20Configuration.md)
- [→ AUDIO DEEP DIVE](../UPDATE/DOC%20LIBRARY/AUDIO%20DEEP%20DIVE%20—%20TWS%20Streaming,%20Sync,%20Reconnection%20Delays%20&%20Glitches.md)
- [→ TWS DEEP DIVE](../UPDATE/DOC%20LIBRARY/TWS%20DEEP%20DIVE%20—%20Reconnect%20Lag,%20Bud%20Identity,%20MAC%20Strategy,%20and%20Risks.md)
