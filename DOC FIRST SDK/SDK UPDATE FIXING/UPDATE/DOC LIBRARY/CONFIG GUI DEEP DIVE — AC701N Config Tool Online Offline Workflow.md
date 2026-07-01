# CONFIG GUI DEEP DIVE — AC701N Config Tool Online Offline Workflow

**Board:** JL7016G Hybrid (BR28)  
**SDK:** FIRST PERIORITY SDK  
**Scope:** How the config GUI works offline and online, transport path (SPP/USB/UART), generated bin files, and whether anything compiles on-board.

---

## 1. Executive Answer

Your config GUI workflow is **tool-driven on PC**, not compilation on earbuds.

- GUI tools generate config/resource binaries on PC, such as `cfg_tool.bin`, `eq_cfg_hw.bin`, `anc_gains.bin`, `anc_coeff.bin`.
- These binaries are then packed into flash images (`jl_isd.fw`, `update.ufw`) or written online to flash areas.
- Earbuds only **read/write flash/config data** at runtime. They do **not compile code** on device.

So the answer to your question is:
- **Generate bin file:** Yes, on PC.
- **Save updated bin into firmware/update package:** Yes.
- **Compile on board:** **No**.

---

## 2. Your GUI Entry Project (.jlxproj)

Primary launcher:
- [cpu/br28/tools/AC701N_配置工具入口(Config Tools Entry).jlxproj](cpu/br28/tools/AC701N_配置工具入口(Config%20Tools%20Entry).jlxproj)

This launcher defines buttons for:
- Config Tool (generate `cfg_tool.bin`)
- Audio Effect Tool (generate `eq_cfg_hw.bin`)
- ANC Designer (generate `anc_gains.bin`, `anc_coeff.bin`)
- FW Editing Tool (name/resources in FW/UFW)
- Touch debug tool

Key behavior in this file:
- It checks required package tools (`eq`, `efftool`, `sdktool`, `luaconfig`, etc.).
- Config generation runs `luaconfig` with project/root/bin/tone paths.
- Effect generation runs `efftool --type eq --async-serial`.

Reference lines:
- package list and launcher wiring in [cpu/br28/tools/AC701N_配置工具入口(Config Tools Entry).jlxproj](cpu/br28/tools/AC701N_配置工具入口(Config%20Tools%20Entry).jlxproj)

---

## 3. Offline Flow (PC build/package path)

## 3.1 What gets generated

Typical generated files from GUI tools:
- `cfg_tool.bin` (main config DB: bt name/mac defaults, key behavior, tones table references, etc.)
- `eq_cfg_hw.bin` (EQ/effect tuning)
- `anc_gains.bin`, `anc_coeff.bin` (ANC parameters)

State sample for config tool is visible in:
- [cpu/br28/tools/cfg_tool_state_complete.lua](cpu/br28/tools/cfg_tool_state_complete.lua)

This file shows exactly the kind of entries you mentioned:
- BT names
- BT/BLE MAC placeholders
- tone table entries
- large sets of CVP/ANC/volume parameters

## 3.2 How offline packaging consumes bins

Packaging/flash scripts include these generated bins in `-res` / reserved areas.

Example script:
- [cpu/br28/tools/download/soundbox/download.bat](cpu/br28/tools/download/soundbox/download.bat)

It calls `isd_download.exe` with resources including:
- `tone.cfg`
- `cfg_tool.bin`
- `eq_cfg_hw.bin`
- `p11_code.bin`

Then builds update artifacts:
- `jl_isd.fw`
- `update.ufw` via `ufw_maker.exe`

Main tool-side build script also extracts overlays and builds app image:
- [cpu/br28/tools/download.bat](cpu/br28/tools/download.bat)

You can see it generates binaries from `sdk.elf` (`aac.bin`, `aptx.bin`, etc.) and then invokes download packaging flow.

## 3.3 Where these files are placed in flash

`isd_config.ini` defines flash mapping/reserved behavior:
- [cpu/br28/tools/isd_config.ini](cpu/br28/tools/isd_config.ini)

Notable entries:
- VM area (`VM_LEN = 8K`)
- ANC areas:
  - `ANCIF_FILE = anc_gains.bin`
  - `ANCIF1_FILE = anc_coeff.bin`

This is why ANC tool outputs map directly into reserved flash partitions.

---

## 4. Online Flow (No rebuild, runtime flash update)

Online mode is implemented by firmware protocol handlers, not by recompiling firmware.

Core handler:
- [apps/common/config/new_cfg_tool.c](apps/common/config/new_cfg_tool.c)
- Protocol definitions:
  [apps/common/config/include/cfg_tool.h](apps/common/config/include/cfg_tool.h)

Supported online ops include:
- Query basic firmware info
- Query file size/content
- Prepare write file (get flash addr, erase unit)
- Read address range
- Erase address range
- Write address range
- Enter upgrade mode

These correspond to command IDs in `cfg_tool.h` (`ONLINE_SUB_OP_*`).

## 4.1 What online write really does

The tool sequence is:
1. Ask firmware for target file physical address and erase unit.
2. Read aligned flash range around that file.
3. Modify needed bytes on PC.
4. Send erase+write commands back.

This behavior is explicitly documented in comments in:
- [apps/common/config/include/cfg_tool.h](apps/common/config/include/cfg_tool.h)

For `cfg_tool.bin`, firmware accumulates writes and triggers reset after completed write range in:
- [apps/common/config/new_cfg_tool.c](apps/common/config/new_cfg_tool.c)

So online save is a controlled flash patch, not a code build.

---

## 5. Communication Channels: SPP, USB, UART, BLE

## 5.1 Actual supported transport in this project

Project transport options are macro-defined in board config:
- [apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h)

Defined types:
- `TCFG_UART_COMM`
- `TCFG_USB_COMM`
- `TCFG_SPP_COMM`

Current defaults in your board file:
- `TCFG_CFG_TOOL_ENABLE = DISABLE`
- `TCFG_EFFECT_TOOL_ENABLE = DISABLE`
- `TCFG_COMM_TYPE = TCFG_NULL_COMM`

So online tool path is compiled but currently feature-gated off by default.

## 5.2 SPP path (classic BT serial profile)

SPP online bridge:
- [apps/common/third_party_profile/jieli/online_db/spp_online_db.c](apps/common/third_party_profile/jieli/online_db/spp_online_db.c)

It:
- registers SPP callbacks,
- initializes online DB on SPP connect,
- routes packets for cfg/eq channels (`0x12`, `0x05`, `0x11`) into `cfg_tool_online_parse`.

## 5.3 USB CDC path

USB receives framed packets and calls config parser when communication mode is USB:
- [apps/common/device/usb/device/task_pc.c](apps/common/device/usb/device/task_pc.c)

## 5.4 UART path

UART parser supports both old/new packet framing and routes config packets to:
- `online_cfg_tool_data_deal(...)`

File:
- [apps/common/config/ci_transport_uart.c](apps/common/config/ci_transport_uart.c)

## 5.5 BLE COM port question

In this codebase, for config tool specifically:
- There is an enum value `DB_COM_TYPE_BLE` in [apps/common/third_party_profile/jieli/online_db/online_db_deal.h](apps/common/third_party_profile/jieli/online_db/online_db_deal.h),
- but there is **no BLE online_db transport implementation file** like `ble_online_db.c` in this SDK tree,
- and active tool routing is through SPP/USB/UART handlers.

Conclusion for this SDK snapshot:
- "BLE COM port" for this config workflow is **not implemented as a dedicated BLE GATT transport path** here.
- Effective online config transport is SPP (classic BT serial), USB CDC, or UART.

---

## 6. Where name/MAC/tone values are consumed in firmware

`cfg_tool.bin` items are exposed through syscfg APIs and IDs:
- [include_lib/system/syscfg_id.h](include_lib/system/syscfg_id.h)

Examples:
- `CFG_BT_NAME` (101)
- `CFG_BT_MAC_ADDR` (102)
- `CFG_BLE_NAME` (103)
- `CFG_BLE_MAC_ADDR` (104)

So when GUI updates those fields and data is packaged or online-written, firmware reads them through syscfg interfaces at runtime/boot.

---

## 7. Online vs Offline: Practical Difference

Offline:
- Generate bins on PC.
- Repack firmware/update package.
- Flash/update device.
- Best for production release and full reproducibility.

Online:
- Keep current firmware running.
- Use SPP/USB/UART tool protocol to read/erase/write target flash regions.
- Fast iteration for tuning (EQ/ANC/config values).
- Still writes flash data; no code compilation.

---

## 8. Does this trigger recompilation?

No. Two distinct layers:

1. **Compile/link layer (PC):**
- `winmk.bat all` compiles C and links `sdk.elf`.

2. **Config/resource layer (PC tools + runtime flash update):**
- GUI tools generate/update bin files.
- Bin data gets packaged into FW/UFW or written online.

Earbuds execute existing firmware and load updated config data; they do not compile source.

---

## 9. Current State in Your Project (important)

From your board config:
- AAC + LDAC are enabled.
- Config GUI online features are default-disabled unless you explicitly enable tool macros and choose transport mode.

Relevant file:
- [apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h](apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h)

If you want active online GUI tuning path, you must enable the corresponding macros (`TCFG_CFG_TOOL_ENABLE`/`TCFG_EFFECT_TOOL_ENABLE`) and select communication mode (`USB`, `UART`, or `SPP`).

---

## 10. Final Conclusion

Your `.jlxproj` config ecosystem is a complete PC-side configuration pipeline:
- GUI edits -> bin generation -> pack/flash or online flash patch -> firmware reads updated values.

It is exactly suitable for configurable items like:
- BT name
- BT/BLE MAC defaults
- tone mapping/resources
- EQ curves
- ANC parameters

And the key point:
- **No on-board compilation occurs**. Only data update and runtime load.

---

**Document ID:** CFG-GUI-DEEPDIVE-AC701N-2026-001  
**Status:** Complete ✅

---

## Related FIX Records

| Fix | Title | Relevance |
|-----|-------|-----------|
| [FIX-005](../../FIXING/FIX-005%20—%20BLE%20MAC%20Address%20Ignored%20at%20Boot.md) | BLE MAC address ignored at boot | Config GUI MAC vs `user_cfg.c` |
| [FIX-006](../../FIXING/FIX-006%20—%20Hardcoded%20Buddie%20Name%20Overwrites%20Config%20GUI%20Name.md) | Hardcoded name overwrites Config GUI name | Config GUI BT name field |
