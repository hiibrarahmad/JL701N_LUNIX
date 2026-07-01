---
tags: [fix, linker-error, codeblocks, online-debug, fft-pca]
date: 2026-04-22
status: COMPLETE & DEPLOYED
severity: ERROR (blocks link)
---

# FIX-003 — Undefined References For online_db And FFT/PCA Symbols

## Error Summary

Link failed with undefined references such as:
- app_online_db_ack
- app_online_db_register_handle
- pca_open
- a2dp_opened
- transcription_opened
- mic_insert_data
- spk_insert_data
- package_undone_count / package_done_offset / send_buffer

## Root Cause

There were two separate causes:

1. Missing symbol provider in active project build list
- `cpu/br28/fft_and_pca.c` was not included in `AC701N.cbp`.
- Its global symbols (`pca_open`, `a2dp_opened`, `transcription_opened`, `mic_insert_data`, etc.) were referenced from other files but never linked.

2. online_db symbols compiled out when `APP_ONLINE_DEBUG == 0`
- `apps/common/third_party_profile/jieli/online_db/online_db_deal.c` wraps real implementation in `#if APP_ONLINE_DEBUG`.
- Callers still compile in this SDK configuration, producing unresolved symbols at link stage.

## Fix Applied

### A. Added missing source to Code::Blocks project
File: `AC701N.cbp`
- Added `cpu/br28/fft_and_pca.c`
- Added `cpu/br28/fft_and_pca.h`

### B. Ensured linker object list includes FFT/PCA object
File: `cpu/br28/tools/sdk.elf.objs.txt`
- Inserted `obj/Release/cpu/br28/fft_and_pca.o`

### C. Added safe fallback stubs for non-online-debug builds
File: `apps/common/third_party_profile/jieli/online_db/online_db_deal.c`
- Added `#else` branch under `#if APP_ONLINE_DEBUG` with no-op / fail-safe stubs for:
  - `app_online_get_buf_remain`
  - `app_online_db_send_more`
  - `app_online_db_send`
  - `app_online_db_ack`
  - `app_online_db_register_handle`
  - `app_online_get_api_table`
  - `app_online_putchar`, `app_online_puts`, `app_online_put_u8hex`, `app_online_put_u16hex`, `app_online_put_u32hex`, `app_online_put_buf`

## Verification

Build command executed:
```bat
.vscode/winmk.bat all
```

Result:
- Link completed (`+LINK cpu/br28/tools/sdk.elf`)
- Previous undefined reference errors are gone
- Remaining output shows only linker stack-size warnings (non-blocking)

## Changed Files

- AC701N.cbp
- apps/common/third_party_profile/jieli/online_db/online_db_deal.c
- cpu/br28/tools/sdk.elf.objs.txt
