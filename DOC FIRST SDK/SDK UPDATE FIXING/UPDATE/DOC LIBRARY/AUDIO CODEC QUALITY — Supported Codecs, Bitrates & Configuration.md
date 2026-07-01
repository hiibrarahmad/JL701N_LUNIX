# Audio Codec Quality — Supported Codecs, Bitrates & Configuration

**Document Version:** 1.0  
**Board:** JL7016G Hybrid (BR28 core)  
**Firmware:** AC701N.cbp  
**Last Updated:** April 2026  

---

## Executive Summary

The AC701N BR28 SDK includes support for **7 distinct audio codecs** across two use cases:
- **A2DP Music:** SBC (active), AAC (enabled), LDAC (enabled), aptX (infrastructure present, inactive)
- **HFP Calls:** mSBC (active), CVSD (encoder-only), LC3 (library present, disabled)

**Current Configuration (JL7016G Hybrid):**
- **A2DP codec state:** SBC + AAC + LDAC are enabled in firmware; runtime selection depends on source-device negotiation
- **DAC output:** 32 kHz sample rate (all music)
- **Current upgrade state:** AAC and LDAC are already enabled in board config

---

## A2DP Music Codecs

### 1. SBC (Subband Codec) — **✅ ENABLED (Default)**

#### Overview
- **Status:** Fully enabled and hardware-accelerated
- **Quality:** Bluetooth standard; high fidelity at bitpool 38
- **Use Case:** Wireless music streaming from phones

#### Configuration

| Parameter                 | Value                            | Source                                                                                       |
| ------------------------- | -------------------------------- | -------------------------------------------------------------------------------------------- |
| **Enable Macro**          | `TCFG_DEC_SBC_ENABLE = ENABLE`   | [board_jl7016g_hybrid_cfg.h:1053](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L1053) |
| **Hardware Acceleration** | `CONFIG_SBC_CODEC_HW`            | [AC701N.cbp:48](AC701N.cbp#L48)                                                              |
| **Library**               | `sbc_eng_lib.a`                  | [AC701N.cbp:216](AC701N.cbp#L216)                                                            |
| **Bitpool Setting**       | 38 (`__set_sbc_cap_bitpool(38)`) | [earphone.c:1418](apps/earphone/earphone.c#L1418)                                            |

#### Bitrate & Quality Calculation

| Property | Value |
|----------|-------|
| **Sample Rate** | 16, 32, 44.1, 48 kHz |
| **Channel Mode** | Mono, Dual, Stereo, **Joint Stereo** (active) |
| **Subbands** | 4 or **8** (active) |
| **Blocks** | 4, 8, 12, **16** (active) |
| **Allocation Method** | Loudness or **SNR** (active) |
| **Bitpool Value** | **38** |

**Effective Bitrate at 44.1 kHz, Joint Stereo, 8 subbands, 16 blocks, bitpool=38:**
$$
\text{Bitrate} = 4 \times 8 \times 16 \times 38 = 19,456 \text{ bits per frame}
$$
$$
\text{Frame duration} = \frac{8 \times 16}{44.1 \text{ kHz}} = 2.9 \text{ ms}
$$
$$
\text{Effective bitrate} = \frac{19,456}{2.9 \text{ ms}} \approx \boxed{237 \text{ kbps}}
$$

**Quality Assessment:**
- **Hearing-critical band:** ✅ Full fidelity (6–7 kHz detail preserved)
- **Compression ratio:** 1.5:1 (CD-quality PCM @ 16-bit, 44.1 kHz = ~1.4 Mbps → 237 kbps)
- **Listening impression:** Near-transparent; excellent for compressed music (Spotify, Apple Music)
- **Equivalent to:** High-quality MP3 128 kbps or better

#### Buffer & Delay
| Metric | Value | Source |
|--------|-------|--------|
| **BT RX Buffer** | 46 KB (LDAC-enabled build path) | [board_jl7016g_hybrid_cfg.h:970](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L970) |
| **A2DP Buffer (LOW)** | 150 ms | [lib_btctrler_config.c:107](apps/earphone/log_config/lib_btctrler_config.c#L107) |
| **A2DP Buffer (HI)** | 260 ms | [lib_btctrler_config.c:108](apps/earphone/log_config/lib_btctrler_config.c#L108) |
| **Playback Latency (Normal)** | 75 ms | [lib_btctrler_config.c:118](apps/earphone/log_config/lib_btctrler_config.c#L118) |
| **Game Mode Latency** | 47 ms (35 ms + 12 ms) | [lib_btctrler_config.c](apps/earphone/log_config/lib_btctrler_config.c) |

#### CPU Clock Requirements
| Mode | Clock | Purpose |
|------|-------|---------|
| **SBC decode + No EQ** | 48 MHz | Default playback |
| **SBC decode + EQ** | 96 MHz | With EQ enabled |

#### Enabling Game Mode (Low Latency)
Low-latency mode reduces playback delay from 75 ms to 47 ms for gaming:

```c
// In [app_config.h](apps/earphone/include/app_config.h)
#define CONFIG_A2DP_GAME_MODE_ENABLE      1      // Default: 0 (disabled)
#define CONFIG_A2DP_GAME_MODE_DELAY_TIME  35     // Base delay in ms
```

**Trade-off:** Lower buffer threshold increases risk of underrun/glitching on poor RF links.

---

### 2. AAC — **✅ ENABLED**

#### Overview
- **Status:** Library `aac_dec_lib.a` linked and enabled in board config
- **Quality:** Better compression than SBC; preferred by Apple, Android OEM profiles
- **Use Case:** Premium streaming (Tidal, Apple Music lossless setup)
- **Activation:** Already active in current firmware config

#### Configuration

| Parameter | Value | Source |
|-----------|-------|--------|
| **Enable Macro** | `TCFG_BT_SUPPORT_AAC = 1` | [board_jl7016g_hybrid_cfg.h:967](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L967) |
| **Library** | `aac_dec_lib.a` | [AC701N.cbp:259](AC701N.cbp#L259) |
| **FFT Mutex** | `CONFIG_AAC_CODEC_FFT_USE_MUTEX` | [AC701N.cbp:44](AC701N.cbp#L44) |
| **Configured Bitrate** | 131 kbps | [earphone.c:557](apps/earphone/earphone.c#L557) |

#### Quality Specifications

| Property | Value |
|----------|-------|
| **Sample Rates** | 44.1, 48 kHz (standard A2DP) |
| **Channels** | Stereo |
| **Bitrate (Configured)** | 131 kbps |
| **Quality @ 131 kbps** | Good fidelity (slight compression artifacts in 8–16 kHz band) |
| **Equivalent to** | MP3 192–256 kbps (AAC is more efficient) |

**Quality Assessment:**
- **Hearing-critical band:** ⚠️ Slight loss at 8–16 kHz (presence region) due to lower bitrate vs. SBC
- **vs. SBC @ 237 kbps:** AAC @ 131 kbps is more efficient but lower bitrate (39% reduction in transmission)
- **Listening impression:** Very good for streaming audio; transparent to most listeners
- **Device support:** iOS, Android, Windows, macOS

#### Buffer & Delay
| Metric | Value | Source |
|--------|-------|--------|
| **BT RX Buffer** | 5 KB | [app_config.h:358](apps/earphone/include/app_config.h#L358) |
| **A2DP Buffer (LOW)** | 100 ms | [lib_btctrler_config.c:105](apps/earphone/log_config/lib_btctrler_config.c#L105) |
| **A2DP Buffer (HI)** | 250 ms | [lib_btctrler_config.c:106](apps/earphone/log_config/lib_btctrler_config.c#L106) |

**Note:** Game mode disables AAC if active (falls back to SBC):
```c
// In [earphone.c](apps/earphone/earphone.c:558)
#if CONFIG_A2DP_GAME_MODE_ENABLE
  // AAC disabled; use SBC only
#endif
```

#### CPU Clock Requirements
| Mode | Clock | Purpose |
|------|-------|---------|
| **AAC decode** | 48 MHz | Standard A2DP decode |
| **AAC decode (TWS)** | 64 MHz | Dual earbuds synchronization |

#### AAC Current State

AAC is already enabled in the board configuration:

```c
// Line 967
#define TCFG_BT_SUPPORT_AAC                       1
```

Validation steps:
```bash
.vscode/winmk.bat all
```

Runtime verification:
- Pair with AAC-capable phone (iOS, Android)
- Confirm negotiated codec from phone developer options or bt snoop log

---

### 3. LDAC — **✅ ENABLED (Premium Option Active)**

#### Overview
- **Status:** Library `ldac_dec_lib.a` linked and enabled in board config
- **Quality:** **Lossless or near-lossless** at high sample rates (96 kHz)
- **Bitrate:** Up to 990 kbps (3× SBC) at 96 kHz
- **Use Case:** Sony Xperia, Premium Android devices with LDAC support
- **Activation:** Already active in current firmware config (+46 KB RX buffer path)

#### What is LDAC?

LDAC is a **Sony proprietary codec** for Bluetooth audio that provides:
- **Adaptive bitrate:** 660 kbps (96 kHz), 507 kbps (48 kHz), 303 kbps (44.1 kHz)
- **Sampling:** Up to **96 kHz** (vs. 48 kHz for AAC/SBC)
- **Claim:** Lossless/near-lossless at highest bitrate (~3× CD-quality bandwidth)

#### Configuration

| Parameter                  | Value                      | Source                                                                                                     |
| -------------------------- | -------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **Enable Macro**           | `TCFG_BT_SUPPORT_LDAC = 1` | [board_jl7016g_hybrid_cfg.h:968](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L968)                 |
| **Library**                | `ldac_dec_lib.a`           | [AC701N.cbp:232](AC701N.cbp#L232)                                                                          |
| **Supported Sample Rates** | 44.1, 48, 88.2, **96 kHz** | [earphone.c:566](apps/earphone/earphone.c#L566), [avctp_user.h:619](include_lib/btstack/avctp_user.h#L619) |

#### Buffer Requirements
| Metric | Value | Source |
|--------|-------|--------|
| **BT RX Buffer (LDAC mode)** | **46 KB** | [board_jl7016g_hybrid_cfg.h:971](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L971) |
| **BT RX Buffer (SBC/AAC)** | 22 KB | [board_jl7016g_hybrid_cfg.h:974](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L974) |
| **Difference** | +24 KB (2.1× overhead) | — |

**Note:** LDAC activation automatically switches RX buffer from 22 KB → 46 KB:
```c
// In [board_jl7016g_hybrid_cfg.h](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L970)
#if TCFG_BT_SUPPORT_LDAC
#define CONFIG_BT_RX_BUFF_SIZE  (46 * 1024)
#else
#define CONFIG_BT_RX_BUFF_SIZE  (22 * 1024)
#endif
```

#### CPU Clock Requirements
| Mode | Clock | Purpose |
|------|-------|---------|
| **A2DP (no EQ)** | 48 MHz | Standard SBC/AAC |
| **A2DP (stereo EQ)** | 48 MHz | With EQ path |

**LDAC CPU overhead:** Not explicitly documented; likely **64+ MHz** (similar to AAC on TWS).

#### Quality Assessment

| Bitrate | Sample Rate | Quality | Use Case |
|---------|-------------|---------|----------|
| **990 kbps** | 96 kHz | Near-lossless | Audiophile; studio monitoring |
| **660 kbps** | 96 kHz | Lossless (claimed) | High-resolution audio files |
| **507 kbps** | 48 kHz | Lossless (claimed) | CD-quality + overhead |
| **303 kbps** | 44.1 kHz | Near-lossless | Standard music streaming |

**vs. SBC @ 237 kbps:**
- LDAC @ 303 kbps: **+28% bitrate, lossless quality** (better for critical listening)
- LDAC @ 660 kbps: **+178% bitrate, studio-quality** (if link supports)

**Limitations:**
- **Device support:** Primarily Sony (Xperia, WH-1000XM series), limited Android OEM adoption
- **RF link:** Requires stable RSSI > -70 dBm for 660 kbps (vs. -85 dBm for SBC)
- **Game mode:** Disabled when LDAC active (latency ~100+ ms)

#### LDAC Current State

LDAC is already enabled in the board configuration:

```c
// Line 968
#define TCFG_BT_SUPPORT_LDAC                      1
```

Build-time effect (automatic):
```c
// This will auto-adjust on build
#if TCFG_BT_SUPPORT_LDAC
#define CONFIG_BT_RX_BUFF_SIZE  (46 * 1024)  // ← Automatically selected
#endif
```

Validation steps:
```bash
.vscode/winmk.bat all
```

Runtime verification:
- Sony Xperia phone or WH-1000XM headphones
- Monitor RX buffer (should not overflow; adjust thresholds if needed)

---

### 4. aptX — **⚠️ INFRASTRUCTURE PRESENT, NO ENABLE FLAG**

#### Overview
- **Status:** Overlay binary + QMF library linked, but **no board-level enable macro**
- **Quality:** Premium (apt-X Limited) at ~352 kbps
- **Use Case:** Qualcomm-licensed devices; non-standard in stock SDK

#### Technical Status

| Component              | Status      | Source                                                                                                         |
| ---------------------- | ----------- | -------------------------------------------------------------------------------------------------------------- |
| **QMF Filter Library** | ✅ Linked    | [sdk.map:611](cpu/br28/tools/sdk.map#L611) (`libSplittingFilter_pi32v2_OnChip.a`)                              |
| **Stack Symbol**       | ✅ Present   | [sdk.elf.resolution.txt:10285](cpu/br28/tools/sdk.elf.resolution.txt#L10285) (`__set_support_aptx_flag`)       |
| **Overlay Binary**     | ✅ Extracted | [download.bat:40](cpu/br28/tools/download.bat#L40) (`aptx.bin`)                                                |
| **Board Macro**        | ❌ None      | No `TCFG_BT_SUPPORT_APTX` in [board_jl7016g_hybrid_cfg.h](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h) |
| **Runtime Flag**       | ❌ Inactive  | [lib_media_config.c:112](apps/earphone/log_config/lib_media_config.c#L112) (`config_aptx_dec_use_malloc = 0`)  |

#### aptX Specifications (Reference)

| Property | Value |
|----------|-------|
| **Bitrate** | 352 kbps (fixed) or 360 kbps |
| **Sample Rate** | 44.1, 48 kHz |
| **Compression Ratio** | 4:1 (CD-quality) |
| **Latency** | 32 ms (aptX-LL variant: 40 ms) |
| **Quality** | Near-transparent; professional audio (Technics, Pioneer) |

#### Why aptX is Disabled
1. **Licensing:** Qualcomm requires per-board approval
2. **No public board flag:** SDK doesn't expose user-selectable aptX macro
3. **Fallback behavior:** Uses SBC/AAC instead

#### Enabling aptX (Advanced Users)

This requires **internal SDK changes** and **Qualcomm licensing approval**:

**Hypothetical steps:**
1. Add board macro (requires SDK source access from vendor)
2. Negotiate aptX licensing with Qualcomm
3. Rebuild with flag set

**Not recommended for production unless:**
- You have pre-negotiated aptX license
- You have access to JL internal SDK modifications
- Your deployment requires aptX devices (rare in consumer market)

---

## HFP Call Codecs

### 5. mSBC — **✅ ENABLED (Wideband Calls)**

#### Overview
- **Status:** Fully enabled; standard for modern Bluetooth calls
- **Quality:** **Wideband (16 kHz)**; rich voice clarity
- **Use Case:** All HFP phone calls via Bluetooth
- **Activation:** Automatic for BR28 (disabled on BR21)

#### Configuration

| Parameter | Value | Source |
|-----------|-------|--------|
| **Decoder Enable** | `TCFG_DEC_SBC_ENABLE = ENABLE` | [board_jl7016g_hybrid_cfg.h:1053](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L1053) |
| **Encoder Enable** | `TCFG_ENC_MSBC_ENABLE = ENABLE` | [board_jl7016g_hybrid_cfg.h:1058](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L1058) |
| **Hardware Acceleration** | `CONFIG_MSBC_CODEC_HW` | [AC701N.cbp:49](AC701N.cbp#L49) |
| **Stack Flag** | `__set_support_msbc_flag(1)` | [earphone.c:554](apps/earphone/earphone.c#L554) |
| **Chip Requirement** | BR28 (enabled); BR21 forces mSBC OFF | [earphone.c:552–554](apps/earphone/earphone.c#L552) |

#### Specifications

| Property | Value |
|----------|-------|
| **Sample Rate** | **16,000 Hz** (wideband) |
| **Voice Band** | 50–4000 Hz (vs. CVSD 50–3400 Hz) |
| **Bitrate** | ~57.6 kbps |
| **Frame Size** | 120 samples / 7.5 ms |
| **Compression** | Modified SBC (same algorithm as A2DP SBC, adjusted for voice) |
| **Quality vs. CVSD** | +18% bandwidth (16 kHz vs. 8 kHz) → **noticeably clearer** |

#### CPU Clock Requirements
| Mode | Clock | Source |
|------|-------|--------|
| **mSBC call** | 80 MHz | [board_jl7016g_hybrid_cfg.h:1136](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L1136) |
| **Advanced call** | 96 MHz | [board_jl7016g_hybrid_cfg.h:1136](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L1136) |

#### Quality Assessment
- **Hearing impression:** Natural, warm voice; superior to narrowband (CVSD)
- **Speech intelligibility:** ✅ Excellent (full frequency content)
- **Background noise:** Better rejection (frequency content above 3.4 kHz helps distinguish speech from noise)

#### Device Compatibility
- ✅ iOS 11+
- ✅ Android 5.0+ (most devices)
- ✅ Windows Phone
- ✅ Desktop Bluetooth adapters (Windows, macOS)
- ✅ Modern car head units

**Fallback:** Phone automatically downgrade to CVSD if mSBC not supported (rare on modern phones).

---

### 6. CVSD — **⚠️ ENCODER ENABLED, DECODER DISABLED**

#### Overview
- **Status:** Encoder ON (transmission), Decoder OFF (no incoming support)
- **Quality:** **Narrowband (8 kHz)**; basic voice communication
- **Use Case:** Legacy fallback for ancient phones (pre-2015)
- **Strategy:** Enable transmission for compatibility; disable reception (unnecessary overhead)

#### Configuration

| Parameter | Value | Source |
|-----------|-------|--------|
| **Decoder Enable** | `TCFG_DEC_CVSD_ENABLE = DISABLE` | [board_jl7016g_hybrid_cfg.h:1054](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L1054) |
| **Encoder Enable** | `TCFG_ENC_CVSD_ENABLE = ENABLE` | [board_jl7016g_hybrid_cfg.h:1059](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L1059) |

#### Specifications

| Property | Value |
|----------|-------|
| **Sample Rate** | **8,000 Hz** (narrowband) |
| **Voice Band** | 50–3400 Hz |
| **Bitrate** | ~64 kbps |
| **Frame Size** | 60 samples / 7.5 ms |
| **Coding** | Continuously Variable Slope Delta |

#### Quality Assessment
- **Hearing impression:** Thin, tinny voice; acceptable for speech intelligibility
- **vs. mSBC @ 16 kHz:** **-53% frequency content** (missing 3.4–16 kHz presence region)
- **Use case:** Last-resort fallback only

#### CPU Clock Requirements
| Mode | Clock | Source |
|------|-------|--------|
| **CVSD call** | 64 MHz | [board_jl7016g_hybrid_cfg.h:1134](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L1134) |

#### Why Encoder Only?
Modern phones (≥iOS 5, ≥Android 2.1) support mSBC; CVSD reception is unnecessary. Keeping encoder enables fallback if phone rejects mSBC offer.

---

### 7. LC3 (LE Audio) — **❌ DISABLED (Future BLE Calls)**

#### Overview
- **Status:** Library `lc3_codec_lib.a` linked but decoder disabled
- **Quality:** Low-latency, high-fidelity voice (24 kHz option)
- **Use Case:** Bluetooth LE audio calls (BLE instead of classic BR/EDR)
- **Timeline:** Requires BLE audio stack implementation (not yet active)

#### Specifications

| Parameter | Value | Source |
|-----------|-------|--------|
| **Decoder Enable** | `TCFG_DEC_LC3_ENABLE = DISABLE` | [board_jl7016g_hybrid_cfg.h:1055](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L1055) |
| **Library** | `lc3_codec_lib.a` | [AC701N.cbp:229](AC701N.cbp#L229) |
| **Supported Channels** | **2** (stereo, configured) | [lib_media_config.c](apps/earphone/log_config/lib_media_config.c) |
| **Frame Duration** | 25 ms (also supports 50, 100 ms) | [lib_media_config.c](apps/earphone/log_config/lib_media_config.c) |
| **Max Sample Rate** | **≤48 kHz** | [lib_media_config.c](apps/earphone/log_config/lib_media_config.c) |
| **Quality Config** | **4/Max** (range 1–4) | [lib_media_config.c](apps/earphone/log_config/lib_media_config.c) |
| **Stack Symbol** | Present: `a2dp_source_lc3_codec` | [sdk.elf.resolution.txt:10577](cpu/br28/tools/sdk.elf.resolution.txt#L10577) |

#### LC3 Overview (Reference)

LC3 is a **next-generation Bluetooth codec** from the Bluetooth SIG for LE Audio:

| Bitrate | Sample Rate | Use Case | Quality |
|---------|-------------|----------|---------|
| **24 kbps** | 16 kHz | Voice calls | Good intelligibility |
| **32 kbps** | 16 kHz | Voice quality | Near-transparent |
| **64 kbps** | 24 kHz | Premium voice | Excellent |
| **96 kbps** | 48 kHz | Music | High fidelity |
| **160 kbps** | 48 kHz | Lossless | Professional |

**Advantages over mSBC:**
- ✅ Lower latency (≤20 ms vs. 40 ms mSBC)
- ✅ Better compression (32 kbps for phone-quality vs. 57.6 kbps mSBC)
- ✅ Flexible bitrate (codec adapts to link quality)

#### Why LC3 is Disabled
1. **BLE Audio stack:** Requires Bluetooth 5.2 LE audio profile implementation (not integrated yet)
2. **Device support:** Limited to newest phones (iPhone 15.1+, select Android devices)
3. **Fallback:** Classic BR/EDR (mSBC) is sufficient for current market

#### Future Enablement

To activate LC3 (when BLE audio stack is available):

```c
// In [board_jl7016g_hybrid_cfg.h](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L1055)
#define TCFG_DEC_LC3_ENABLE                 ENABLE  // Change from DISABLE
```

---

## Comparison Table

### Music Codecs (A2DP)

| Codec | Status | Bitrate | Sample Rate | Quality | HW Accel | Game Mode | Notes |
|-------|--------|---------|-------------|---------|----------|-----------|-------|
| **SBC** | ✅ Active | ~237 kbps | 44.1/48 kHz | Near-transparent | ✅ Yes | ✅ Supported | Default |
| **AAC** | ✅ Enabled | 131 kbps | 44.1/48 kHz | Good | ❌ No | ⚠️ Disabled if GM | Negotiated with source |
| **LDAC** | ✅ Enabled | 303–990 kbps | 44.1/48/88.2/96 kHz | Lossless | ❌ No | ❌ Disabled if game mode | Negotiated with source |
| **aptX** | ⚠️ Inactive | 352 kbps | 44.1/48 kHz | Near-transparent | ? | ? | Requires licensing |

### Call Codecs (HFP/eSCO)

| Codec | Status | Bitrate | Sample Rate | Quality | Chip | Notes |
|-------|--------|---------|-------------|---------|------|-------|
| **mSBC** | ✅ Active | ~57.6 kbps | 16 kHz | Wideband (excellent) | BR28 | Preferred |
| **CVSD** | ⚠️ Enc-only | ~64 kbps | 8 kHz | Narrowband (basic) | All | Fallback TX |
| **LC3** | ❌ Disabled | 24–160 kbps | 16/24/48 kHz | Premium | — | Future BLE audio |

---

## Recommendations for JL7016G Hybrid

### Default Configuration (Current)
✅ **Recommended for general use**
- **A2DP:** SBC @ 237 kbps (near-transparent quality, universal device support)
- **HFP:** mSBC @ 16 kHz (wideband calls, modern phones)
- **CPU:** 48–96 MHz (music + EQ)

### For Premium Audio Experience
🎧 **AAC and LDAC are already active in build**

**If targeting Sony/audiophile devices:**
1. Keep `TCFG_BT_SUPPORT_LDAC = 1` in [board_jl7016g_hybrid_cfg.h:968](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L968)
2. Monitor RX buffer (auto-switches to 46 KB)
3. Test with Sony Xperia or WH-1000XM devices

**If targeting Apple/generic Android:**
1. Keep `TCFG_BT_SUPPORT_AAC = 1` in [board_jl7016g_hybrid_cfg.h:967](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L967)
2. Bitrate is lower (131 kbps) but more efficient
3. Support for ~85% of modern phones

### For Gaming (Low Latency)
🎮 **Enable Game Mode**
```c
// In [app_config.h](apps/earphone/include/app_config.h)
#define CONFIG_A2DP_GAME_MODE_ENABLE      1       // Default: 0
#define CONFIG_A2DP_GAME_MODE_DELAY_TIME  35      // ms
```
- Latency: 75 ms → 47 ms (28 ms reduction)
- Codec: SBC only (AAC/LDAC disabled)
- Trade-off: Smaller buffer → higher glitch risk on poor RF

---

## Configuration Reference

### Files to Modify

| File | Section | Macro | Purpose |
|------|---------|-------|---------|
| [board_jl7016g_hybrid_cfg.h](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L967) | Line 967 | `TCFG_BT_SUPPORT_AAC` | Enable/disable AAC |
| [board_jl7016g_hybrid_cfg.h](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h#L968) | Line 968 | `TCFG_BT_SUPPORT_LDAC` | Enable/disable LDAC |
| [app_config.h](apps/earphone/include/app_config.h#L268) | Line 268 | `CONFIG_A2DP_GAME_MODE_ENABLE` | Enable game mode (low latency) |
| [app_config.h](apps/earphone/include/app_config.h#L269) | Line 269 | `CONFIG_A2DP_GAME_MODE_DELAY_TIME` | Base latency for game mode |

### Building After Changes

```bash
cd d:\jl7016g final approach\SDKS\FIRST PERIORITY SDK
.vscode/winmk.bat clean
.vscode/winmk.bat all
```

---

## Appendix: Codec Technical Details

### SBC Bitpool Explanation

Bitpool is a parameter that controls SBC compression:
- **Bitpool = 38** (current): Bitrate ~237 kbps @ 44.1 kHz
  - ✅ Recommended range (Bluetooth A2DP spec suggests 2–53)
  - ✅ Maintains near-transparent quality
  
- **Lower bitpool:** Reduces bitrate but increases compression artifacts
  - Bitpool = 20: ~125 kbps (noticeable loss at 6–8 kHz)
  
- **Higher bitpool:** Increases bitrate but exceeds typical link rates
  - Bitpool = 50+: >300 kbps (requires excellent RF link, 2 Mbps data rate)

### LDAC Adaptive Bitrate Negotiation

When both earbuds are active (TWS mode), LDAC may reduce bitrate to maintain RF stability:

| Condition | Bitrate | Sample Rate |
|-----------|---------|-------------|
| Excellent RF (RSSI > -50 dBm) | 990 kbps | 96 kHz |
| Good RF (RSSI > -70 dBm) | 660 kbps | 96 kHz |
| Fair RF (RSSI > -80 dBm) | 303 kbps | 44.1 kHz |
| Poor RF (RSSI < -85 dBm) | Falls back to SBC | 44.1 kHz |

### AAC vs. SBC Efficiency

| Aspect | AAC | SBC |
|--------|-----|-----|
| **Bitrate for "good" quality** | ~100–150 kbps | ~200–250 kbps |
| **Compression ratio** | 10:1 to 12:1 | 6:1 to 8:1 |
| **CPU load** | Higher (FFT) | Lower (HW accel) |
| **Latency** | 40–50 ms | 20–30 ms |
| **Device support** | ~90% | ~100% |

---

## Summary

The **JL7016G BR28** firmware supports a full range of audio codecs:

1. **Active Codecs:**
  - 🎵 **SBC** (A2DP music): ~237 kbps, universal fallback, excellent quality
  - 🎵 **AAC** (A2DP music): 131 kbps target profile, broad phone compatibility
  - 🎵 **LDAC** (A2DP music): 303–990 kbps, premium quality path
  - 📞 **mSBC** (HFP calls): 16 kHz wideband, natural voice

2. **Negotiation Note:**
  - Phone capability and link quality decide final A2DP codec at runtime

3. **Infrastructure Present:**
   - 🎵 **aptX**: Overlay + library linked, no public enable flag (licensing required)

4. **Future Ready:**
   - 📞 **LC3** (LE Audio): Library present, awaiting BLE audio stack integration

**Recommendation:** Keep AAC + LDAC enabled, then validate runtime negotiation behavior on your target phones and tune buffer/latency policy for your product profile.

---

**Document ID:** AUDIO-CODEC-QUAL-2026-001  
**Status:** Complete ✅  
**Next Steps:** Validate codec negotiation matrix across your target phone models (SBC/AAC/LDAC) and record interoperability results.
