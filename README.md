<p align="center">
  <a href="README.md">English</a> | <a href="README.zh_CN.md">简体中文</a>
</p>

# AI EARBUD BY IBRAR AHMAD

This repository contains the firmware source code and technical documentation for AI EARBUD BY IBRAR AHMAD, suitable for development boards based on the JieLi AC701N chip. This firmware solution is specifically designed for **low-power real-time audio transmission** and features a built-in efficient audio compression module.

## Project Modification Note

This repository is not a stock SDK drop. It includes project-specific modifications made for the JL7016G Hybrid earphone target, including firmware fixes, board configuration corrections, touch handling repairs, microphone bring-up fixes, TWS behavior investigation, and documentation updates.

The main working area for deep notes and fix records is:

- `DOC FIRST SDK/SDK UPDATE FIXING/`

## Modification Tracker

| ID | Modification | Main Area | Status |
|----|--------------|-----------|--------|
| 001 | Fixed missing `TCFG_IMU_SENSOR_PWR_PORT` board macro build error | Board config | Done |
| 002 | Fixed `lis2de12` driver object/file mismatch at link time | Build system | Done |
| 003 | Fixed undefined references for online DB / FFT / PCA related symbols | Build system | Done |
| 004 | Verified TWS bring-up depends on real L/R hardware split on `PC5` | TWS | Verified |
| 005 | Fixed BLE MAC from config not being applied at boot | Bluetooth | Done |
| 006 | Fixed hardcoded Bluetooth name overriding configured product name | App init | Done |
| 007 | Fixed PB4 touch gestures being detected but dropped before app actions | Touch | Done |
| 008 | Fixed CH3 long/hold touches being suppressed by long-by-res gating | Touch | Done |
| 009 | Fixed PB4 valid touch range being rejected by low algorithm ceiling | Touch | Done |
| 010 | Fixed in-ear remap hook interfering even when ear-detect was disabled | In-ear / touch | Done |
| 011 | Fixed UART debug framing/setup mismatch during touch bring-up | Debug / UART | Done |
| 012 | Fixed main MIC power path from unused PA0 MICLDO to PA2 MICBIAS | Audio / MIC | Done |
| 013 | Fixed MIC0 mode mismatch by changing main MIC to single-ended cap mode | Audio / MIC | Done |
| 014 | Increased max playback volume by raising JL7016G Hybrid ANC digital ceiling from `-17 dB` to `-6 dB` | Audio / volume | Done |

For the full tracker and deep-dive notes, see:

- `DOC FIRST SDK/SDK UPDATE FIXING/UPDATE/DOC LIBRARY/00 - SDK Progress Tracker.md`
- `DOC FIRST SDK/SDK UPDATE FIXING/UPDATE/DOC LIBRARY/BOARD — JL7016G Hybrid Config Deep Study.md`

When used together with our open-source mobile AI application, the following core functions can be achieved:

- Real-time transcription of spoken content
- Voice interaction with the AI assistant via the headphones
- Transcription of both your own and others' speech during online meetings

## 🛠 System Requirements

- **Operating System:** Windows 10 or later (64-bit system recommended)
- **Hardware:** 
  - JieLi AC701N development board
  - Forced download tool
- **Other:** USB **data cable** (type-A)

## 📚 Preparation

For this project, we recommend using VSCode for compilation in a Windows environment. The environment setup process is as follows:

1. [Configure the development environment on Windows](#1-configure-windows-development-environment)  
2. [Development environment in VSCode](#2-build-sdk-in-vscode)
3. [Burn firmware using the forced download tool](#3-burn-firmware-using-the-forced-download-tool)

### 1 Configure Windows Development Environment

This SDK project is designed **specifically for Windows systems** and uses **Code::Blocks** as the default development environment.

The entire configuration process is divided into three main steps:

1. **Download and install [the Windows version of Code::Blocks](https://pkgman.jieliapp.com/s/codeblocks)**

2. **Open Code::Blocks for the first time and close it immediately**  
   This operation will generate the necessary configuration files for subsequent development.

3. **Download and install [the latest JieLi Windows toolchain](https://pkgman.jieliapp.com/s/win-toolchain)**  
   [Click here to download]

After completing the above steps, you can open the Code::Blocks project and start compiling and developing. (It is recommended to use VSCode for compilation and development.)

If you need more toolchains and post-processing tools, please refer to: **[Latest tool versions](https://doc.zh-jieli.com/Tools/zh-cn/other_info/index.html)**.

For more detailed information about development tools, please click the link below:  
https://doc.zh-jieli.com/Tools/zh-cn/dev_tools/dev_env/index.html

### 2 Build SDK in VSCode

Building in VSCode is done by invoking the `make` command.

#### 2.1 Open the project in VSCode at the SDK root directory
<p align="center">
  <img src="../image/firmware/firmware_open_vscode.jpg" width="400" />
</p>

#### 2.2 Install the necessary extensions: **Task Explorer** and **C/C++**

<p align="center">
  <img src="../image/firmware/firmware_vscode_task.jpg" width="400" />
</p>

<p align="center">
  <img src="../image/firmware/firmware_vscode_c_cpp_ext.jpg" width="400" />
</p>
