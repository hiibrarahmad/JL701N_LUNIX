---
tags: [reference, glossary, acronyms, definitions]
date: 2026-05-05
---

# Glossary — Acronyms & Abbreviations

All technical terms used across the JL7016G Hybrid SDK documentation, in alphabetical order.

---

## A

**A2DP** — Advanced Audio Distribution Profile. Bluetooth profile for streaming stereo audio from a phone to earphones.

**ADC** — Analog-to-Digital Converter. Converts analog signals (e.g. microphone audio) into digital samples for the DSP.

**ANC** — Active Noise Cancellation. Uses a feedforward/feedback microphone to generate an anti-noise signal, reducing ambient sound perceived by the ear.

**AVCTP** — Audio/Video Control Transport Protocol. The low-level transport used by AVRCP to carry media control commands (play, pause, next, volume) over Bluetooth.

**AVRCP** — Audio/Video Remote Control Profile. Bluetooth profile that lets earphones send media control commands to a phone (play/pause, next/prev, volume) and receive absolute volume notifications back.

---

## B

**BLE** — Bluetooth Low Energy. A low-power Bluetooth radio used for device pairing advertisements, OTA firmware updates, and app control (separate from BT Classic A2DP/HFP).

**BT** — Bluetooth (Classic). The 2.4 GHz radio used for A2DP audio streaming and HFP hands-free calls.

**BT Classic** — See BT. Specifically refers to the EDR-capable Bluetooth stack (as opposed to BLE).

---

## C

**CH1** — CTMU Channel 1. Connected to PB1 (Port B pin 1). Configured as in-ear detection reference. After FIX-018 this channel generates GPIO output only (no app key events).

**CH3** — CTMU Channel 3. Connected to PB4 (Port B pin 4). The primary user-control touch sensor — handles music, volume, and call events.

**CTMU** — Capacitive Touch Measurement Unit. The on-chip hardware block that drives the LP touch key system. Measures capacitance changes on PB1 (CH1) and PB4 (CH3).

**CVP** — Communication Voice Processing. The SDK's voice/call audio processing pipeline including noise suppression, echo cancellation, and AGC for HFP calls.

---

## D

**DAC** — Digital-to-Analog Converter. Converts digital audio samples from the DSP into analog audio output driving the speaker (earphone driver).

**DCDC** — DC-to-DC switching regulator. A more efficient but noisier power supply alternative to LDO. The JL7016G Hybrid board currently uses LDO (see `TCFG_LOWPOWER_POWER_SEL = PWR_LDO15`).

**DSP** — Digital Signal Processing. The audio processing engine inside the BR28 core that handles EQ, ANC, CVP, and codec decoding.

---

## E

**EDR** — Enhanced Data Rate. The high-throughput mode of Bluetooth Classic used for A2DP audio streaming (up to 3 Mbps vs 1 Mbps for basic rate).

**EQ** — Equalizer. Audio filter that adjusts the frequency response of the speaker output. Configurable via the AC701N Config GUI tool.

**eSCO** — Extended Synchronous Connection-Oriented link. The Bluetooth transport used for two-way voice audio during HFP calls (as opposed to ACL for data).

---

## G

**GPIO** — General Purpose Input/Output. A configurable digital pin that can be read (input) or driven (output) by firmware. PC3 is used as a GPIO output for PB1 touch feedback.

---

## H

**HFP** — Hands-Free Profile. Bluetooth profile for phone calls — handles call state (incoming, active, outgoing), audio routing, microphone, and AT commands for Siri/Google Assistant.

---

## I

**IIS / I2S** — Inter-IC Sound. Serial audio interface used between the BR28 SoC and external audio codecs or amplifiers.

---

## K

**KEY_2** — The app-layer key identifier assigned to PB4 (CH3, `key_value = 2`). The primary control key handling music, volume, and call events.

**KEY_EVENT_FROM_TWS** — A flag set in `event->arg` by the TWS layer when an event was forwarded from the slave bud to the master. Used in `key_tws_lr_diff_deal()` to determine which physical bud was touched.

**KWS** — Keyword Spotting. Always-on voice wake-word detection engine. Disabled on JL7016G Hybrid (`TCFG_SMART_VOICE_ENABLE = DISABLE_THIS_MOUDLE`).

---

## L

**LDO** — Low Drop-Out voltage regulator. A linear regulator used for the system power supply on this board. Simpler and less noisy than DCDC but less efficient.

**LP** — Low Power. Used to refer to the LP touch key system (`lp_touch_key.c`) which drives the CTMU channels.

**LRC** — Low-frequency RC oscillator. The low-power clock source used during sleep/low-power states (`TCFG_LOWPOWER_OSC_TYPE = OSC_TYPE_LRC`).

**lr_diff_otp_deal()** — SDK function implementing the runtime L/R bud differentiation dispatch. Called by `key_tws_lr_diff_deal()`. The `otp` in the name refers to "option" (not One-Time Programmable in this context).

---

## M

**MAC** — Media Access Control address. The 6-byte unique hardware address identifying each Bluetooth device. In TWS, each bud needs a distinct MAC and a sibling MAC provisioned at flash time.

**MICBIAS** — Microphone Bias voltage. A DC voltage (typically 1.5–2.5 V) supplied by the SoC to power the microphone capsule's internal FET. Correct MICBIAS is required for any audio signal at all.

---

## O

**OTA** — Over The Air. Wireless firmware update mechanism. The build produces `update.ufw` (full) and `jl_isd.bin` (download image) for OTA delivery.

**OTP** — One-Time Programmable. A memory region burned permanently into the chip at manufacture time. **Not** what `otp` means in `lr_diff_otp_deal()` — see that entry.

---

## P

**PA0 / PA1 / PA2** — Port A pins 0, 1, 2. GPIO pins on the SoC. PA2 is used as MICBIAS power output after FIX-012.

**PB1** — Port B pin 1. The in-ear detection touch pad (CH1). After FIX-018, generates PC3 GPIO output only — no app key events.

**PB4** — Port B pin 4. The primary user-control touch pad (CH3, KEY_2). Handles all music/volume/call gestures.

**PC3** — Port C pin 3. GPIO output driven by PB1 touch state. After FIX-019: idle = HIGH, touch = LOW (active-LOW).

**PC5** — Port C pin 5. Hardware TWS channel-select pin. Pulled to a specific voltage to identify Left vs Right bud to the SoC.

---

## S

**SDK** — Software Development Kit. The full JL701N firmware source tree provided by JieLi (JL).

**SoC** — System on Chip. The single integrated circuit containing the CPU, DSP, Bluetooth radio, and peripherals. The SoC on this board is the AC701N with a BR28 RISC core.

---

## T

**TCFG_** — "Target Configuration" prefix. All board-level feature enable/disable macros in `board_jl7016g_hybrid_cfg.h` use this prefix.

**TWS** — True Wireless Stereo. Two-bud earphone system where both buds connect independently to the phone (or one connects and relays audio to the other via a BT link between the buds).

**TWS_FUNC_ID_VOL_SYNC** — The function identifier used when packing a TWS inter-bud data message carrying volume levels. Handled by the receiving bud to set its local DAC.

**tws_api_send_data_to_sibling** — SDK API that sends a data packet to whichever peer bud is currently connected, regardless of master/slave role. Used in `bt_tws_sync_volume()` after FIX-020.

**tws_api_send_data_to_slave** — SDK API that sends a data packet from master to slave only. Does not work when called from the slave (no-op). Replaced by `tws_api_send_data_to_sibling` in FIX-020.

---

## U

**UART** — Universal Asynchronous Receiver/Transmitter. Serial communication interface used for debug logging. Correct settings: 1000000 baud, 8N1 (see FIX-011).

**UFW** — Update Firmware. The `.ufw` file format produced by the JL build system for OTA wireless updates.

---

**Back to:** [→ REFERENCE/](./README.md) | [→ Main Documentation Hub](../README.md)
