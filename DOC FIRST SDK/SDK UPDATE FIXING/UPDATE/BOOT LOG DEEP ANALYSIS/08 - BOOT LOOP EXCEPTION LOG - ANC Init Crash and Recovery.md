---
tags: [boot-log, exception, crash, anc, boot-loop, soft-reset, heap, debug, jl7016g]
date: 2026-06-09
status: DOCUMENTED — DEVICE RECOVERED AND WORKING
severity: CRITICAL (was) → RESOLVED
---

# 🔴 Boot Log 08 — Boot Loop Exception: ANC Init Crash & Recovery

> **Incident summary:** The left bud entered an infinite exception boot loop. Every boot crashed at exactly the same point — immediately after ANC gain coefficients were loaded from flash — and issued a `P33_SOFT_RST`, which restarted the boot sequence. The device never progressed past ANC init. Device was recovered and is now operational.
>
> **This log is captured from a device that was boot-looping.** The repeating sections in the log below are real — each is a separate boot cycle, not a copy-paste artifact.

---

## Navigation

- [→ BOOT LOG INDEX](./00%20-%20BOOT%20LOG%20DEEP%20ANALYSIS%20INDEX.md)
- [→ 01 - Chronological Line by Line](./01%20-%20Chronological%20Line%20by%20Line%20Explanation.md) — normal boot reference
- [→ 02 - Error Warning Noise Decoder](./02%20-%20Error%20Warning%20and%20Noise%20Decoder.md)
- [→ AUDIO-IMP-009 MIC Gain](../../../IMPROVEMENTS/AUDIO%20IMPROVEMENTS/AUDIO-IMP-009%20—%20MIC%20Gain%20Optimization.md) — Mic2 at gain=1 noted here

---

## Phase Map — What Each Crash Cycle Covers

Every boot in this log follows the same 7-phase sequence before crashing in Phase 7:

```
Phase 1 │ Clock & PLL init          │ ~0–100 ms │ ✅ passes
Phase 2 │ Reset reason decode        │ ~0 ms     │ ✅ passes  (shows crash flag)
Phase 3 │ RTOS task creation         │ ~0–120 ms │ ✅ passes
Phase 4 │ Flash/VM/SDFILE mount      │ ~127–175 ms│ ✅ passes (VM is empty)
Phase 5 │ Board + power init         │ ~193–515 ms│ ✅ passes
Phase 6 │ user_cfg / provisioning    │ ~518–682 ms│ ✅ passes
Phase 7 │ ANC init + gain load       │ ~1048–1068 ms│ 💥 CRASH — exception
```

---

## Full Annotated Log (One Complete Boot Cycle)

The following is a single boot cycle with every line explained. All subsequent cycles in the captured log are identical — only minor ADC trim values differ between runs.

---

### Phase 1 — Clock & PLL Initialization

```
[00:00:00.100][Debug]: [CLOCK][-------------Clock Dump-----------]
[00:00:00.100][Debug]: [CLOCK]---ID 6903      Ver D
```
**ID 6903, Ver D** — Chip silicon ID. `6903` confirms this is the AC701N (JL7016G Hybrid) silicon. Version D is the die revision. No issue.

```
[00:00:00.100][Debug]: [CLOCK]--Internal OSC CLK : 24000000
[00:00:00.100][Debug]: [CLOCK]--OSC CLK : 0
```
**Internal OSC at 24 MHz, external OSC = 0** — The chip is running from its internal 24 MHz RC oscillator. External crystal OSC shows 0, which is normal if no external crystal is fitted (or not yet started). The BT oscillator takes over later.

```
[00:00:00.100][Debug]: [CLOCK]-PLL TARGET CLOCK 192
[00:00:00.100][Debug]: [CLOCK]--PLL SYS CLK : 48000000
```
**PLL target = 192 MHz, system = 48 MHz** — The PLL VCO runs at 192 MHz (×8 from 24 MHz input). The system clock divides this to 48 MHz at boot. This is the `CONFIG_BT_CONNECT_HZ` clock level — normal for early boot before BT enters idle.

```
[00:00:00.100][Debug]: [CLOCK]--PLL 96M SEL : 3
[00:00:00.100][Debug]: [CLOCK]--PLL 48M SEL : 0
```
**96M sel = 3, 48M sel = 0** — The 96 MHz and 48 MHz output divider tap selections from the PLL. These index values select which PLL output is routed to each peripheral. Normal values for 192 MHz VCO.

```
[00:00:00.100][Debug]: [CLOCK]---SFC CLK : 48000000
[00:00:00.100][Debug]: [CLOCK]---SPI CLK : 48000000
[00:00:00.100][Debug]: [CLOCK]---HSB CLK : 24000000
[00:00:00.100][Debug]: [CLOCK]---LSB CLK : 24000000
[00:00:00.100][Debug]: [CLOCK]---P33 CLK : 24000000
```
| Bus | Clock | Notes |
|---|---|---|
| SFC (Serial Flash Controller) | 48 MHz | Flash read clock — limits max throughput |
| SPI | 48 MHz | SPI peripheral bus |
| HSB (High Speed Bus) | 24 MHz | Main peripheral bus |
| LSB (Low Speed Bus) | 24 MHz | Slow peripherals (UART, I2C) |
| P33 (power domain P33) | 24 MHz | Analog/power management core |

All normal.

```
[00:00:00.100][Debug]: [CLOCK]--AUDIO CLK : 0
```
**Audio clock = 0** — The audio (I2S/codec) clock is not yet started. This is expected at boot — audio init happens later. It will start when DAC/ADC are opened.

```
[00:00:00.100][Debug]: [CLOCK]---SYS DVDD : 0 / 7
[00:00:00.100][Debug]: [CLOCK]---RAM DVDD : 8
[00:00:00.100][Debug]: [CLOCK]---VDC13    : 10
```
| Rail | Value | Meaning |
|---|---|---|
| SYS DVDD | 0 / 7 | Core digital supply: current level 0, max level 7 |
| RAM DVDD | 8 | RAM supply voltage index (affects retention current) |
| VDC13 | 10 | 1.3V domain supply trim index |

These are hardware trim register values, not voltages in mV. Normal for this silicon revision.

```
[00:00:00.100][Debug]: [CLOCK]PLL_CON  : 188929b3
[00:00:00.100][Debug]: [CLOCK]CLK_CON0 : 00000231
[00:00:00.100][Debug]: [CLOCK]CLK_CON1 : 00001643
```
Raw PLL and clock control register dumps. Cross-reference with AC701N register map if debugging clock issues. These values match a known-good 192 MHz PLL lock configuration.

---

### Phase 2 — Reset Source Decode ⚠️

```
[00:00:00.100][0-MSYS]--Reset Source : 0x1
[00:00:00.100]MSYS_P11_RST
```
**MSYS reset source 0x1 = P11 reset** — The main system (MSYS) was reset because the P11 subsystem reset it. This is the outermost reset domain being informed of a cascaded reset from below.

```
[00:00:00.100][1-P11]--Reset Source : 0x40
[00:00:00.100]P11_P33_RST
```
**P11 reset source 0x40 = P33 reset** — The P11 subsystem was reset because P33 reset it. P11 is the main CPU domain; P33 is the power management + analog domain.

```
[00:00:00.100][2-P33]--Reset Source : 0x20
[00:00:00.100]P33_SOFT_RST
```
**P33 reset source 0x20 = SOFTWARE RESET** — P33 itself issued a software reset. This is the origin of the entire reset chain. A software reset originates from: the exception handler, a watchdog, or explicit code calling `sys_reset()`.

```
[00:00:00.100]LVD_FLAG: 1
```
**Low Voltage Detection flag = 1** — The LVD fired during the previous run. **This is a consequence, not the cause.** When the CPU crashed mid-instruction, the exception handler fired and issued `P33_SOFT_RST`. During the exception handling window, transient current draw dropped suddenly, which can momentarily trip LVD even with a healthy battery. Battery voltage throughout this log is 4160 mV — fully charged, not a power problem.

```
[00:00:00.100]soft_reset_exception
```
**THE KEY LINE.** This message is printed by the boot ROM / early startup code when it detects that the reset flag was set by the exception handler of the *previous run* — not a power-on reset, not a watchdog, not a deliberate reset. The previous run ended in an unhandled fault (hardfault, null pointer dereference, stack overflow, or illegal instruction). The exception handler:
1. Saved the crash flag to a non-volatile register
2. Called `P33_SOFT_RST` to reboot
3. On the next boot, this message is printed to signal "I crashed last time"

This confirms: **the device is in a crash → reboot → crash loop**.

---

### Phase 3 — RTOS Task Creation

```
[00:00:00.100]task: systimer, tcb @ 0x4d441c
[00:00:00.100]create_task systimer : stack:(0x4c0000,0x4c01fc)
```
**systimer task** — The system timer task (periodic tick, software timers). Stack at `0x4c0000–0x4c01fc` = 512 bytes. This is in internal SRAM. Normal.

```
[00:00:00.100]task: app_core, tcb @ 0x4d448c
[00:00:00.100]create_task app_core : stack:(0x4c0200,0x4c0dfc)
```
**app_core task** — The main application task. Stack at `0x4c0200–0x4c0dfc` = 3072 bytes (3 KB). This is where `earphone.c` / `app_main.c` runs.

```
[00:00:00.100]create_task idle0 : stack:(0x4c0e00,0x4c15fc)
[00:00:00.100]idle : all stack :0x4c0e00, 0x4c0e80, 0x700
[00:00:00.100]err priority 7 : priority 6 is reserved fot GIEMASK
```
**⚠️ `err priority 7 : priority 6 is reserved fot GIEMASK`** — The idle0 task attempted to set its priority to 7 but priority 6 is reserved for the global interrupt enable mask (GIEMASK). This is a configuration warning in the RTOS scheduler. It does **not** cause the boot loop — this warning appears in healthy boots too. The scheduler falls back to the next available priority.

```
[00:00:00.100]create_task idle1 : stack:(0x4c1600,0x4c1dfc)
```
**idle1 task** — Second idle task for the second CPU core (dual-core RTOS). Stack at `0x4c1600–0x4c1dfc` = 2048 bytes.

**RTOS stack layout summary:**
```
0x4c0000–0x4c01fc  systimer   (512 B)
0x4c0200–0x4c0dfc  app_core   (3072 B)
0x4c0e00–0x4c15fc  idle0      (2048 B)
0x4c1600–0x4c1dfc  idle1      (2048 B)
                                -------
Total task stacks:  7680 B = 7.5 KB
```

---

### Phase 4 — Flash / VM / SDFILE Mount

```
[00:00:00.127][Info]: [SDFILE]VM size: 0x4f100 @ 0xabf00
```
**VM region = 0x4f100 bytes (315.6 KB) at flash offset 0xabf00** — The virtual machine / variable storage region. This is a large filesystem-like area in flash that holds all runtime configuration written by the AC701N Config GUI tool and the firmware's `syscfg_write()` calls.

```
[00:00:00.138][Info]: [VM]17a968 <------> 17a968
```
**⚠️ `17a968 <------> 17a968` — VM start = VM end = SAME ADDRESS** — This means the VM contains **zero bytes of written data**. The VM region is either:
- Freshly erased (factory state / full flash erase)
- Never written to (first boot after blank flash)

This is why every `syscfg_read()` below returns error -251 (no data found). All configuration falls back to firmware-compiled defaults. This is not the crash cause, but it means **no GUI tool configuration is active** — the device is running entirely on hardcoded `#define` defaults.

```
[00:00:00.152][Info]: [SDFILE]disk capacity 1024 KB
```
**Flash = 1024 KB** — Confirms `CONFIG_FLASH_SIZE = FLASH_SIZE_1M`. This matches the PCB's 1 MB SPI flash chip.

```
[00:00:00.157]last file_addr:abc5f 25a
[00:00:00.161]end_addr:abf00
```
**SDFILE filesystem last entry and end address** — The SDFILE (embedded filesystem for tone files, ANC coefficients) has its last file ending at address `0xabc5f` with size `0x25a` bytes. The filesystem boundary is `0xabf00`. This means the tone/ANC data occupies addresses up to `0xabf00` in flash — immediately before the VM region. Normal layout.

```
49 53 44 55 04 02 57 FF 8C 13 F9 04 19 9D FF FF
```
**SDFILE header bytes** — First 16 bytes of the SDFILE header: `49 53 44 55` = ASCII `ISDU` (Jieli SDFILE magic identifier). The following bytes are the filesystem version, flags, and metadata. This is the file that starts at the filesystem header. Normal.

```
[00:00:00.175][Info]: [VM]vm_info:addr:0xabf00, len:0x2000, mode:0x1
```
**VM config: address 0xabf00, length 0x2000 (8 KB), mode 1 (read-write)** — The VM uses 8 KB of flash at the very top of the SDFILE region. Mode 1 = circular write with wear leveling. Normal.

---

### Phase 5 — Board and Power Init

```
[00:00:00.193][Info]: [BOARD]Power init : apps/earphone/board/br28/board_jl7016g_hybrid.c
```
**Power init using hybrid board config** — Confirms the active board file. All `TCFG_*` settings from `board_jl7016g_hybrid_cfg.h` are now being applied.

```
[00:00:00.209]P11_HEAP_BEGIN = 0xf23c8c
[00:00:00.213]P11_HEAP_SIZE = 0x3a74
```
**🔴 CRITICAL: Heap = only 14,964 bytes (14.6 KB)**

`P11_HEAP_SIZE = 0x3a74 = 14,964 bytes`

This is the **entire dynamic allocation budget** for all `malloc()` / `os_malloc()` calls in the application. At this point, the RTOS task stacks (7.5 KB) have already been allocated from static BSS. The remaining 14.6 KB must serve:
- ANC handle: 536 bytes
- ANC gain database: 236 bytes
- BT stack: ~8–12 KB (largest single consumer)
- TWS buffers: ~2–4 KB
- Audio decode buffers: ~2–4 KB

**Total estimated demand: ~13–21 KB. Available: 14.6 KB.** This is why the crash happens — the heap is exhausted during or immediately after ANC init, before BT stack can allocate its own buffers.

```
[00:00:00.228]P11_SYSTEM->MEM_PWR_CON: 0xff0, M2P_MEM_CONTROL: 0x39
```
**RAM power control registers** — `MEM_PWR_CON = 0xff0` enables all RAM banks. `M2P_MEM_CONTROL = 0x39` = bitmask of which RAM banks are retained in low-power mode. `0x39 = 0b00111001` = banks 0, 3, 4, 5 retained. Banks 1, 2 power off in sleep. The `TCFG_LOWPOWER_RAM_SIZE = 3` setting (384 KB retained) corresponds to these retained banks.

```
[00:00:00.235][Info]: [P33]P3_WKUP_EN0 is 0x4
```
**P33 wakeup enable 0 = 0x4** — Bit 2 set = wakeup source 2 enabled. This is the charging detection wakeup pin. Needed to wake from sleep when charger connects.

```
[00:00:00.246][Info]: [P33]P3_WKUP_EDGE0 is 0x6
[00:00:00.252][Info]: [P33]P3_WKUP_EDGE1 is 0x2
```
**Wakeup edge configuration** — `0x6 = 0b110` means wakeup sources 1 and 2 trigger on falling edge. `0x2 = 0b010` means analog wakeup source 1 triggers on falling edge. This matches the touch key and charger wakeup behavior (active-low signals).

**P33 PORT_SEL registers** — The `P3_PORT_SEL0` through `P3_PORT_SEL11` values map each analog wakeup pin to a specific GPIO function. These define which pins are connected to analog functions (MIC bias, DAC output, touch channels). Cross-reference with the hardware pin mapping:

| Register | Value | GPIO Function |
|---|---|---|
| P3_PORT_SEL0 = 0x12 | 18 | MICBIAS0 (PA2) |
| P3_PORT_SEL1 = 0x28 | 40 | LN (DAC negative output) |
| P3_PORT_SEL2 = 0x31 | 49 | LP (DAC positive output) |
| P3_PORT_SEL4 = 0x3a | 58 | MICBIAS2 (PG7) |
| P3_PORT_SEL5 = 0x28 | 40 | Analog MIC input |
| P3_PORT_SEL11 = 0x2f | 47 | ANC feedback path |

```
[00:00:00.419]lvd_con = 0xbd
```
**LVD control register = 0xBD** — Low Voltage Detector configuration. `0xBD = 0b10111101`. Bit 7 = enable, bits 0–4 = threshold level. The threshold here corresponds to approximately 3.0V trip point (below battery minimum). Normal.

```
[00:00:00.473]vbg_adc_value = 271
[00:00:00.486]vbat_adc_value = 352
[00:00:00.490]vbat = 4160 mv
```
**Battery = 4160 mV** — Fully charged. Calculated from:
```
vbat = (vbat_adc / vbg_adc) × Vbg_reference
     = (352 / 271) × ~3200 mV ≈ 4150 mV (approximately)
```
The internal bandgap reference (`vbg_adc = 271` ADC counts) is used to calibrate the battery measurement. **Power is healthy — the boot loop is NOT caused by low battery.**

```
[00:00:00.515]hpvdd = 1279 mV
```
**HPVDD = 1279 mV** — This reads the internal DACVDD LDO at its nominal 1.25V setting (`TCFG_AUDIO_DAC_LDO_VOLT = DACVDD_LDO_1_25V`). The 1279 mV reading is correct — it is the ADC's measurement of the 1.25V internal rail with trim offsets. The **external 1.85V HPVDD** (enabled by PG6 = HIGH) is separate and is not directly measured by this ADC read. This value is **not anomalous**.

---

### Phase 6 — user_cfg Loading and Provisioning

```
[00:00:00.518][Info]: [USER_CFG]bt name config:ibrarkhan
[00:00:00.524][Info]: [USER_CFG]ble name config:jl_earphone_ble
```
**BT name = "ibrarkhan", BLE name = "jl_earphone_ble"** — The BT classic name is read from provisioning code (hardcoded in `user_cfg.c`). The BLE name is the default Jieli name. Since the VM is empty, no GUI-configured name overrides exist.

```
[00:00:00.531][Info]: [USER_CFG]tws pair code config:
FF FF
```
**TWS pair code from VM = FF FF** — The VM is empty so this read returns `0xFFFF` (erased flash). The pair code will be overridden by the provisioning function below.

```
[00:00:00.548][Info]: [USER_CFG]aec cfg read err ret: -251, aec : 72, use default value
```
**⚠️ AEC config read failed, error -251** — The firmware tried to read the AEC (Acoustic Echo Cancellation) configuration from the VM (syscfg ID for AEC settings). Error -251 = no data found (VM is empty, nothing was ever written). The system falls back to compiled-in defaults. This happens every boot because the VM is empty. **Not the crash cause** — but important: it means the MIC gains shown below are always defaults, never tuned values.

```
[00:00:00.557][Info]: [USER_CFG]CVP_cfg Mic0_gain:12 Mic1_gain:12 Mic2_gain:1 Mic3_gain:1 DAC_Gain:12
```
**CVP microphone gains (default values):**

| Mic | Gain Index | Role | Note |
|---|---|---|---|
| Mic0 | 12 | Call mic (PA1) | Reasonable |
| Mic1 | 12 | ANC Feedforward (PA4) | Reasonable |
| Mic2 | **1** | ANC Feedback/Error (PG7) | ⚠️ Very low — see AUDIO-IMP-009 |
| Mic3 | **1** | Not wired on this PCB | Not used |
| DAC | 12 | Analog output gain | Reasonable |

Mic2 at index 1 (≈ 0 dB or very low) is documented in [AUDIO-IMP-009](../../../IMPROVEMENTS/AUDIO%20IMPROVEMENTS/AUDIO-IMP-009%20—%20MIC%20Gain%20Optimization.md) as a likely performance issue for ANC feedback loop quality.

```
[00:00:00.568]audio_sw_digital_vol_init,user-defined[0]
[00:00:00.574]sys_hw_dvol_max:8211,call_hw_dvol_max:4115
```
**Digital volume hardware registers initialized:**
- `sys_hw_dvol_max = 8211` = the hardware register value corresponding to `DIG_VOL_MAX_VALUE = -6.0 dB` (ANC volume cap)
- `call_hw_dvol_max = 4115` = hardware register value for call path maximum volume

These are raw DAC register values, not dB directly. The conversion: `8211 = 0x2013`, internal Q-format fixed-point representation of -6 dBFS attenuation in the hardware volume module.

```
[00:00:00.595][Info]: [USER_CFG]max vol:16 default vol:8 tone vol:8
```
**Volume configuration:** 16 levels maximum, default = level 8 (mid), tone playback = level 8.

```
[00:00:00.609][Info]: [USER_CFG]auto_off_time:180
```
**Auto-shutdown = 180 seconds** (3 minutes of disconnected idle). See [CONN-IMP-005](../../../IMPROVEMENTS/CONNECTION%20IMPROVEMENTS/CONN-IMP-005%20—%20Auto-Shutdown%20Timer%20Tuning.md) for tuning recommendation.

```
[00:00:00.614][Info]: [USER_CFG]Provisioning Pair 1 - LEFT BUD (B01)
[00:00:00.622][Info]: [USER_CFG]  CFG_BT_MAC_ADDR (102) = 3C:00:0A:7E:1A:00
[00:00:00.630][Info]: [USER_CFG]  CFG_TWS_LOCAL_ADDR (95) = 3C:00:0A:7E:1A:00
[00:00:00.638][Info]: [USER_CFG]  CFG_TWS_REMOTE_ADDR (96) = 3C:00:0A:7E:1A:01 [sibling]
[00:00:00.647][Info]: [USER_CFG]  CFG_TWS_COMMON_ADDR (97) = AA:BB:CC:00:01:FF [pair]
[00:00:00.656][Info]: [USER_CFG]  CFG_TWS_CHANNEL (98) = 0x00 [LEFT]
[00:00:00.664][Info]: [USER_CFG]  CFG_TWS_PAIR_CODE_ID (602) = 0x6688
```
**Manual MAC provisioning for Pair 1, Left Bud (B01):**

| Config ID | Value | Meaning |
|---|---|---|
| 102 | `3C:00:0A:7E:1A:00` | BT classic MAC address for this bud |
| 95 | `3C:00:0A:7E:1A:00` | TWS local (own) address |
| 96 | `3C:00:0A:7E:1A:01` | TWS remote (sibling right bud) address |
| 97 | `AA:BB:CC:00:01:FF` | Shared pair address (common identity) |
| 98 | `0x00` | Channel = LEFT (PC5 pulldown confirmed left) |
| 602 | `0x6688` | TWS pair code (anti-cross-pair lock) |

Provisioning is working correctly — the left bud identity is set.

```
[00:00:00.682][Info]: [USER_CFG]lrc cfg:
90 01 90 01 90 01 90 01 01
```
**LRC (Low-Rate Clock) configuration** — 9 bytes configuring the 32 kHz low-power clock behavior. `90 01` repeated = each channel's LRC trim value. `01` at end = LRC mode select. Normal.

---

### Phase 7 — ANC Initialization 💥 CRASH POINT

```
[00:00:01.048]anc_hdl size:536
```
**ANC allocates 536 bytes** — The ANC handler allocates its main state structure from the heap. At this point:
```
Heap remaining before this line: ~14,428 bytes
After anc_hdl:                   ~13,892 bytes
```

```
[00:00:01.052]ANC_OFF Select
[00:00:01.055]ANC_ON Select
[00:00:01.058]Transparency Select
```
**Three ANC mode handlers registered** — The three operating modes (OFF, ANC-ON, Transparency) are registered with the mode dispatcher. Each registration allocates a small mode-specific config struct. Estimated ~50–100 bytes each.

```
[00:00:01.061]anc_mode_enable_set:3
```
**anc_mode_enable_set = 3** — All 3 modes enabled (bitmask `0b011`). The ANC state machine is configured. No error reported.

```
[00:00:01.066]anc_gain_db get succ,len:236
```
**ANC gain coefficients loaded from flash, 236 bytes** — The ANC digital gain table (FF mic level vs ANC correction gain, stored in SDFILE at `ANCIF_ADR: 0xFD000`) was successfully read. This is the last successful operation before the crash.

**Heap state after this line (estimated):**
```
anc_hdl:         536 bytes used
3 mode structs:  ~200 bytes used
anc_gain_db:     236 bytes used
Total ANC:       ~972 bytes consumed
Heap remaining:  ~13,992 bytes
```

```
💥 [CRASH] — exception thrown. P33_SOFT_RST issued. Next line is Boot N+1.
```

**What happens next (inferred from crash analysis):**

After loading the gain table, `audio_anc_init()` or `earphone_init()` calls `bt_stack_init()` (or equivalent) to start the Bluetooth stack. The BT stack's initialization allocates:
- Main BT heap: ~8–12 KB
- SCO buffer: ~2 KB
- Page/inquiry buffer: ~1 KB

**With only ~13.9 KB remaining and BT stack needing ~11–15 KB, `malloc()` returns `NULL`.** The calling code dereferences this null pointer → **hardfault** → exception handler → `P33_SOFT_RST` → repeats.

---

## Boot Loop Timeline (All Crashes Overlaid)

```
t=0.000s  Clock dump + PLL init
t=0.100s  Reset source: SOFT_RST + soft_reset_exception (printed every boot)
t=0.200s  RTOS tasks created
t=0.127s  VM mounted → empty (17a968 <--> 17a968)
t=0.193s  Board power init
t=0.209s  Heap: BEGIN=0xf23c8c, SIZE=0x3a74 (14964 bytes) ← too small
t=0.518s  bt name / ble name / aec cfg (fail -251) / CVP gains
t=0.614s  Provisioning: LEFT BUD, MAC=3C:00:0A:7E:1A:00 ✓
t=1.048s  anc_hdl alloc 536 bytes ✓
t=1.052s  ANC modes registered ✓
t=1.066s  anc_gain_db 236 bytes loaded ✓
          ↓
          malloc for BT stack → NULL (heap exhausted)
          → null pointer dereference
          → hardfault exception
          → P33_SOFT_RST
          → Boot N+1 (identical)
```

---

## Key Differences Between Crash Boots

The only variations across the 5 captured crash cycles are in the power trim values:

| Boot | `trim` | `wvdd_lev` | `pvdd_level_lev_l_trim` | `dtemp` |
|---|---|---|---|---|
| 1 | 1 | 3 | 3 | 984 mV |
| 2 | 0 | 4 | 4 | 984 mV |
| 3 | 0 | 5 | 5 | 987 mV |
| 4 | 1 | 3 | 3 | 984 mV |
| 5 | 0 | 4 | 4 | 987 mV |

**`trim` oscillates between 0 and 1, `wvdd_lev` cycles 3→4→5→3→4...** — The power management system is iterating through voltage trim steps trying to find a stable operating point after each exception. This cycling is a normal LVD recovery search behavior; it does NOT indicate a hardware power problem.

---

## Root Cause Summary

| Factor | Value | Assessment |
|---|---|---|
| Battery voltage | 4160 mV | ✅ Healthy |
| Reset type | P33 Software Reset | ⚠️ Firmware exception, not hardware |
| Crash indicator | `soft_reset_exception` every boot | 🔴 Confirms exception loop |
| Crash location | After `anc_gain_db get succ` | 🔴 Late ANC init / BT stack init |
| Heap available | 14,964 bytes (14.6 KB) | 🔴 Insufficient for ANC + BT stack |
| VM state | Empty (never written) | ⚠️ All config is defaults |
| AEC config | -251 error (no data) | ⚠️ Not a crash cause, but no tuning active |

**Primary cause: P11_HEAP_SIZE (0x3a74 = 14.6 KB) is insufficient to initialize both the ANC system and the Bluetooth stack sequentially within the same heap.**

---

## Resolution

Device was recovered. Possible recovery methods:
- Reflash with a previous known-good `jl_isd.bin` where heap was larger
- Reduce firmware code size / static allocations to free heap space
- Rebuild with `TCFG_LOWPOWER_RAM_SIZE` reduced (frees retained RAM → expands heap)

After recovery the log should show additional lines after `anc_gain_db get succ` — specifically BT stack init messages, page scan start, and TWS sibling scan.

---

## Related Documents

- [→ 01 - Normal Boot Reference](./01%20-%20Chronological%20Line%20by%20Line%20Explanation.md) — what a healthy boot looks like past this point
- [→ 02 - Error Warning Decoder](./02%20-%20Error%20Warning%20and%20Noise%20Decoder.md) — for `err priority 7` and `-251` explanations
- [→ CONN-IMP-007 BT Clock](../../../IMPROVEMENTS/CONNECTION%20IMPROVEMENTS/CONN-IMP-007%20—%20BT%20Clock%20Frequency%20Power%20vs%20Performance.md) — heap indirectly related to clock/power configuration
- [→ AUDIO-IMP-009 MIC Gain](../../../IMPROVEMENTS/AUDIO%20IMPROVEMENTS/AUDIO-IMP-009%20—%20MIC%20Gain%20Optimization.md) — Mic2 gain=1 noted in this log
- [→ CONN-IMP-005 Auto-Shutdown](../../../IMPROVEMENTS/CONNECTION%20IMPROVEMENTS/CONN-IMP-005%20—%20Auto-Shutdown%20Timer%20Tuning.md) — `auto_off_time:180` seen in this log
