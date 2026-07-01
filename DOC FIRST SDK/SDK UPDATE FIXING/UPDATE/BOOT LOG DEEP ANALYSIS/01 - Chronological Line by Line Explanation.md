# Chronological Line by Line Explanation

This document explains your provided log in time order from power-on until stable phone connection.

Note on style:
- Many lines repeat (same register dump printed twice, repeated reconnect blocks, repeated noise bursts).
- Repeated lines are explained once and marked as repeated behavior to keep this usable while still covering full meaning.

## Phase A: Power-On, Clock Tree, and Reset Cause (0.100s)

### `[CLOCK][-------------Clock Dump-----------]`
Clock diagnostic block begins.

### `[CLOCK]---ID 6903 Ver D`
Chip identification and silicon revision.

### `[CLOCK]--Internal OSC CLK : 24000000`
Internal oscillator is 24 MHz and active as startup source.

### `[CLOCK]--OSC CLK : 0`
External crystal path not selected/used at this moment.

### `[CLOCK]-PLL TARGET CLOCK 192`
PLL target is 192 MHz domain.

### `[CLOCK]--PLL SYS CLK : 48000000`
System PLL-derived clock currently 48 MHz.

### `[CLOCK]--PLL 96M SEL : 3` / `--PLL 48M SEL : 0`
Internal mux selectors for derived PLL branches.

### `[CLOCK]--PLL ALNK CLK : 0`
Audio link PLL subclock disabled at this instant.

### `[CLOCK]---SFC CLK : 48000000`
Serial flash controller at 48 MHz.

### `[CLOCK]---SPI CLK : 48000000`
SPI bus at 48 MHz.

### `[CLOCK]---HSB CLK : 24000000` / `---LSB CLK : 24000000`
High-speed and low-speed bus both at 24 MHz at this snapshot.

### `[CLOCK]---P33 CLK : 24000000`
Always-on/P33 domain clock at 24 MHz.

### `[CLOCK]--USB CLK : 48000000`
USB domain clock prepared at 48 MHz.

### `[CLOCK]--AUDIO CLK : 0`
Audio clock tree not yet enabled.

### `[CLOCK]--UART CLK : 24000000`
UART debug clock at 24 MHz.

### `[CLOCK]--BT CLK : 48000000`
Bluetooth base clock path at 48 MHz.

### `---SYS DVDD : 0 / 7`, `---RAM DVDD : 8`, `---VDC13 : 10`
Power rail trim levels and regulator settings (boot/initial values).

### `---RANGE : 0`, `---TRIM SYS DVDD : 0`
Voltage trim and range info before runtime adaptation.

### `SFC_CON`, `SFC_QCNT`, `SYS_DIV`, `CLK_CONx`, `PLL_CON`, `CON1`, `CON2`, `CMNG_CON0`
Raw hardware register dump. Used for low-level bring-up verification.

### Reset source block
- `[0-MSYS]--Reset Source : 0x1` + `MSYS_P11_RST`
- `[1-P11]--Reset Source : 0x40` + `P11_P33_RST`
- `[2-P33]--Reset Source : 0x1` + `P33_VDDIO_POR_RST`

Meaning:
- Power-on reset propagated through domain hierarchy. This is a clean cold start pattern.

### Duplicate reset/clock lines right after
The same reset summary is printed again by another init stage. Not an error.

## Phase B: Scheduler and Core Tasks (0.100s-0.120s)

### `task: systimer ... create_task systimer`
System timer task created.

### `task: app_core ... create_task app_core`
Main app logic task created.

### `create_task idle0`, `create_task idle1`
Dual-core/dual-idle housekeeping tasks.

### `err priority 7 : priority 6 is reserved fot GIEMASK`
Scheduler warning for reserved priority adjacency; system continues.

### Firmware version banner
`JL701N_V1.6.1-@20240130-$8f8f3995`
Build identity + commit hash.

### `task: sys_event ...`
System event dispatcher task active.

## Phase C: VM and Storage Mount (0.127s-0.192s)

### `[SDFILE]VM size: 0x4f500 @ 0xabb00`
Virtual memory region location and size in flash.

### `[VM]norflash_open() (null) 0 0`
NOR flash backing opened for VM subsystem.

### Address and capacity lines
- `JL_SFC->UNENC_ADRL ...`
- `disk capacity 1024 KB`
- `last file_addr ... end_addr ...`

Meaning:
- Flash translation and file/region boundaries validated.

### Hex bytes after mount
Metadata/signature bytes from filesystem structures.

### `[SDFILE]sdfile mount succ`
Filesystem mount succeeded.

### `[VM]vm_info:addr:0xabb00, len:0x2000, mode:0x1`
VM partition active.

## Phase D: Board Power and P33 IO Setup (0.192s-0.420s)

### `[BOARD]Power init : ... board_jl7016g_hybrid.c`
Board-specific power init function used: JL7016G hybrid board file.

### `P11_HEAP_BEGIN`, `P11_HEAP_SIZE`
Aux domain heap allocated.

### `task: pmu_task`
Power management task starts.

### `MEM_PWR_CON` and `M2P_MEM_CONTROL`
Memory power control register snapshots.

### Large `[P33]` register list (`WKUP`, `AWKUP`, `PORT_SEL`, `APORT_SEL`)
Pin wakeup edges, levels, pending flags, and mux routing for P33 domain.
These lines show your wakeup sources and pin multiplexing profile were loaded.

### `lvd_con`, `trim`, `wvdd_lev`, `pvdd...`
Low-voltage detect and rail trim calibration output.

### ADC sampling lines (`vbg`, `vbat`, `dtemp`, `hpvdd`)
Power/temperature monitoring channel reads:
- `vbat = 3588 mv` indicates battery around 3.59 V during boot.

## Phase E: USER_CFG Load and Runtime Personality (0.511s-0.617s)

### `[USER_CFG]bt name config:ibrarkhan`
Classic BT name loaded from VM.

### `[USER_CFG]ble name config:jl_earphone_ble`
BLE name loaded (not same as EDR name, intentionally separate).

### `[USER_CFG]tws pair code config:` then `FF FF`
Pair code read as 0xFFFF (uninitialized/default), not intended 0x6688.

### `[USER_CFG]rf config:10`
RF power level loaded to max profile.

### `[USER_CFG]sms_dns config:` then `aec cfg read err ret: -251`
AEC profile record missing/invalid; default CVP gains applied.

### `CVP_cfg Mic0_gain:12 ... DAC_Gain:12`
Fallback call-path gains in use.

### `status_config` hexdump and volume lines
UI/tone status table read, max/default/tone volumes configured.

### `warning_tone_v:340 poweroff_tone_v:330`
Battery threshold profile loaded.

### `auto_off_time:180`
Auto shutdown timer set (seconds/min conversion already applied internally).

### `[USER_CFG]mac:` then `BB 0A 2C 77 5B 37`
Active EDR MAC at this run is random/fallback identity.

### `[USER_CFG]lrc cfg:`
Low-rate clock compensation profile loaded.

## Phase F: ANC/Touch/UI/Audio Bring-up (0.983s-2.025s)

### ANC block
`anc_init ok`, mode selections, coeff/gain database loads.

### LP key block
CTMU touch channel thresholds and timing values loaded.

### Update module
`update module init ok` and update parameter processing.

### app main and audio init
`app_main`, `audio_enc_init`, `audio_dec_init`, DAC startup sequence.

### tone playback on boot
`power_on.wts` decoded and sent to DAC.

### Dynamic clock change lines near 1.770s and 2.025s
SYS/RAM DVDD and HSB/SPI clocks shift with runtime mode transitions (tone playback then idle/normal).

## Phase G: Address Dump and Bluetooth Stack Start (2.087s onward)

### `-----edr + ble 's address-----`
Two addresses shown:
- EDR appears as `BB 0A 2C 77 5B 37`
- BLE address shown as separate value (`4C 00 0A 23 1F 12`)

### `btctrler_task_init`, `HCI_LMP init/open`, `bredr_bd_init`
Controller and BR/EDR stack bring-up sequence successful.

### `local_name ibrarkhan`
Controller accepted configured local name.

### BLE init lines
`ble profile init`, `ble name(...)`, advertising sequence counters.

## Phase H: TWS Startup and First Connection Attempt (3s-7s)

### `have tws info`
Stored TWS context exists.

### Page/inquiry enable lines
Device enters discover/connect windows for TWS/phone policy.

### `TWS ... role = 0`
Role 0 context starts (role meaning depends on current state machine role constants in SDK).

### `pend_in`, `accepted_switch_req`, `pend_exit`
Temporary pending period around role/link switching transitions.

### `BT_TWS tws-user ... event=2`
TWS callback event indicates internal state transition.

### Battery sync lines
Sibling battery exchange successful (`set_sibling_bat_level`, `tws_sync_bat_level`).

### `HCI_CREATE_CONNECTION` with target address lines
Outgoing BR/EDR connection attempts to peer addresses.

### `/config.dat Fail` appears
Optional file not found during RCSP/adv path; not fatal to core link stack.

### UI updates
`STATUS_BT_TWS_CONN` indicates TWS link became active.

## Phase I: Timeout/Retry Window (11s-16s)

### `lmp_super_timeout` and reason `8`
First attempted external link timed out.

### Repeated create connection loops
Controller retries connection procedure.

### Later `reason ... fe` then handshake continues
Interim error state followed by successful negotiation.

### Feature/version exchange and role switch success lines
- `LMP_FEATURES...`
- `LMP_SWITCH_REQ`
- `rs_succ:0x1`

Meaning:
- Link layer negotiation and role switch completed successfully.

### Remote name discovery
`REMOTE_NAME : DESKTOP-0UCDMVD` confirms target host identity.

## Phase J: Authentication, Encryption, Phone Link Up (20s-23s)

### SSP / pairing lines
- `Start Public Key` / `End Public Key`
- `Start DH Key` / `End DH Key`
- `LMP_SIMPLE_PAIRING_NUMBER`
- `HCI_EVENT_USER_CONFIRMATION_REQUEST`

Meaning:
- Secure Simple Pairing stage executed.

### Encryption lines
- `LMP_ENCRYPTION_KEY_SIZE_REQ 0x10`
- `LMP_START_ENCRYPTION_REQ`

Meaning:
- 16-byte key path and encrypted link started.

### `BT_STATUS_CONNECTED`
Phone link reaches connected state.

### BLE adv toggles around connected state
Advertising disabled/enabled according to policy and RCSP events.

### `BT_STATUS_FIRST_CONNECTED`
First successful phone connection event latched.

### UI status transitions
`STATUS_BT_CONN` tone and UI change to connected profile.

## Phase K: Audio Prompt and Runtime Steady Behavior (24s+)

### `bt_conn.wts` playback lines
Connection tone decoded and played.

### Clock lines during playback
HSB/SPI boosted again to support audio/tone path.

### AT command snippets
`AT+BRSF`, `AT+BAC`, `AT+CIND`, etc. indicate HFP profile negotiations with phone.

### TWS monitor synchronization lines
`master_start_monitor`, `enter_pure_monitor` show TWS synchronization for phone stream handling.

### Occasional `wtgv2_dec err:64` again
Prompt decode warning reappears; core connection remains intact.

## Interpreting Repeated Noise Characters

Standalone characters and bursts (`P`, `C`, `w`, `%@`) are debug stream artifacts from mixed output contexts.
Treat them as separators/noise unless attached to tagged module messages.

## What This Log Proves

1. Board boot and clock/power initialization are healthy.
2. VM/filesystem mount and USER_CFG load run correctly.
3. TWS stack works (connect/disconnect/retry then stable state reached).
4. Phone BR/EDR connection eventually succeeds with encryption and HFP negotiation.
5. Manual Pair 1 identity is not active in this specific capture (random MAC + pair code FF FF observed).

## What To Check In Your Next Capture

- Presence of provisioning banner line for selected bud build.
- Pair code bytes should map to `0x6688`, not `FF FF`.
- Runtime `mac:` should be `3C:00:0A:7E:1A:00` on left build and `...01` on right build.
- TWS remote/local reciprocal addresses should be visible in provisioning logs.
