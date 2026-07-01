---
tags: [fix, linker-error, build-system, gsensor]
date: 2026-04-22
status: COMPLETE & DEPLOYED
severity: ERROR (blocks link)
---

# FIX-002 — lis2de12 Driver Object Missing At Link

## Error Message

```text
pi32v2-ld.exe: cannot find obj/Release/apps/common/device/gSensor/lis2dh12_driver.o: No such file or directory
```

## Root Cause

A filename typo mismatch existed between the real driver name and the linker/project references:

- Real source files present in repo:
  - apps/common/device/gSensor/lis2de12_driver.c
  - apps/common/device/gSensor/lis2de12_driver.h
- Incorrect references used by build/project metadata:
  - lis2dh12_driver.c/.h
  - lis2dh12_driver.o

The typo is `dh12` vs `de12`. Because of this, the linker requested an object file that is never produced.

## Changes Applied

1. Updated Code::Blocks project entries:
   - File: AC701N.cbp
   - lis2dh12_driver.c -> lis2de12_driver.c
   - lis2dh12_driver.h -> lis2de12_driver.h

2. Updated linker object list entry:
   - File: cpu/br28/tools/sdk.elf.objs.txt
   - lis2dh12_driver.o -> lis2de12_driver.o

## Why This Fix Is Correct

- The actual driver implementation in this SDK is LIS2DE12, not LIS2DH12.
- The Makefile source list already uses lis2de12_driver.c.
- Aligning project/link references with real source names restores a consistent compile+link pipeline.

## Verification Checklist

- [ ] Run .vscode/winmk.bat clean
- [ ] Run .vscode/winmk.bat all
- [ ] Confirm no linker error for lis2dh12_driver.o

## Related Files

- AC701N.cbp
- cpu/br28/tools/sdk.elf.objs.txt
- Makefile
- apps/common/device/gSensor/lis2de12_driver.c
- apps/common/device/gSensor/lis2de12_driver.h
