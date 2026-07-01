---
tags: [fix, ble, mac, identity, earphone]
date: 2026-04-23
status: COMPLETE & DEPLOYED
severity: FUNCTIONAL BUG (BLE identity mismatch)
---

# FIX-005 — BLE MAC Address Set in Config GUI Not Applied at Boot

## Summary

BLE MAC address configured via the AC701N Config GUI Tool was never applied to the hardware.
The device always advertised a derived BLE address calculated from the EDR MAC, ignoring the `CFG_BLE_MAC_ADDR` syscfg value entirely.

---

## Root Cause

In `apps/earphone/earphone.c`, the BLE init block unconditionally derived the BLE MAC from the EDR MAC:

```c
// BEFORE — BLE MAC always derived, CFG_BLE_MAC_ADDR never read
#if (TCFG_BLE_DEMO_SELECT == DEF_BLE_DEMO_ADV)
    memcpy(tmp_ble_addr, (void *)bt_get_mac_addr(), 6);
#else
    lib_make_ble_address(tmp_ble_addr, (void *)bt_get_mac_addr());
#endif
le_controller_set_mac((void *)tmp_ble_addr);
```

`CFG_BLE_MAC_ADDR` (the field set in the GUI and packed into `cfg_tool.bin`) was read by `cfg_file_parse` into syscfg but then never consumed. The BLE controller was always programmed with the auto-derived value.

---

## Fix Applied

`apps/earphone/earphone.c` — BLE init block updated to read `CFG_BLE_MAC_ADDR` first:

```c
// AFTER — use GUI-supplied BLE MAC if valid; fallback to derived address
u8 cfg_ble_addr[6] = {0};
const u8 ff_addr[6]   = {0xff, 0xff, 0xff, 0xff, 0xff, 0xff};
const u8 zero_addr[6] = {0, 0, 0, 0, 0, 0};

#if (TCFG_BLE_DEMO_SELECT == DEF_BLE_DEMO_ADV)
    if (syscfg_read(CFG_BLE_MAC_ADDR, cfg_ble_addr, 6) == 6
        && memcmp(cfg_ble_addr, ff_addr, 6)
        && memcmp(cfg_ble_addr, zero_addr, 6)) {
        memcpy(tmp_ble_addr, cfg_ble_addr, 6);
    } else {
        memcpy(tmp_ble_addr, (void *)bt_get_mac_addr(), 6);
    }
#else
    if (syscfg_read(CFG_BLE_MAC_ADDR, cfg_ble_addr, 6) == 6
        && memcmp(cfg_ble_addr, ff_addr, 6)
        && memcmp(cfg_ble_addr, zero_addr, 6)) {
        memcpy(tmp_ble_addr, cfg_ble_addr, 6);
    } else {
        lib_make_ble_address(tmp_ble_addr, (void *)bt_get_mac_addr());
    }
#endif
le_controller_set_mac((void *)tmp_ble_addr);
```

Validity check: MAC is used only if it is not all-FF (erased flash default) and not all-zero.
If the GUI has not set a BLE MAC, old behavior (derived from EDR) is preserved as fallback.

---

## Files Changed

| File | Change |
|------|--------|
| `apps/earphone/earphone.c` | Added `#include "syscfg_id.h"`, added `syscfg_read(CFG_BLE_MAC_ADDR,...)` with validity guard |

---

## Related: Flash Erase Required

Because VM region persists across flashes by default (`CONFIG_VM_OPT=1`), the old derived address can survive a normal flash. Use the dedicated identity-clean script to force full erase:

```
cpu\br28\tools\download\earphone\download_app_ota_identity_clean.bat
```

This script uses `-format all` so CFG and VM regions are erased and repopulated from the new `cfg_tool.bin` on first boot.

---

## Verification

After flashing with identity-clean script:
1. Forget old pairing on phone/PC (BT caches device names and addresses).
2. Rescan BLE — device should now advertise the MAC address set in the Config GUI.
