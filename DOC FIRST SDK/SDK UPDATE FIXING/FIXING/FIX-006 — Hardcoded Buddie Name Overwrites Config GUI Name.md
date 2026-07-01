---
tags: [fix, bluetooth, name, identity, app_main, earphone]
date: 2026-04-23
status: COMPLETE & DEPLOYED
severity: FUNCTIONAL BUG (BT/BLE name never changes from default)
---

# FIX-006 — Hardcoded "Buddie" Name Overwrites Config GUI Name Every Boot

## Summary

The BT device name set via the AC701N Config GUI Tool (`cfg_tool.bin`) was loaded correctly from flash but then **immediately overwritten** at runtime by a hardcoded `bt_modify_name("Buddie")` call in `app_main.c`.
The device always advertised as "Buddie" regardless of what was configured in the GUI.

---

## Root Cause

In `apps/earphone/app_main.c`, after the earphone application starts (which internally calls `cfg_file_parse` to load `CFG_BT_NAME` and `CFG_BLE_NAME` from `cfg_tool.bin`), the following call was made unconditionally:

```c
bt_modify_name("Buddie");   // ← hardcoded, overwrites cfg_file_parse result
```

Call order at boot:
1. `cfg_file_parse()` → reads name `"ibrarkhan"` from `cfg_tool.bin` into `bt_cfg.edr_name` ✅
2. `bt_modify_name("Buddie")` → pushes `"Buddie"` to BT stack, discarding the loaded name ❌

Because `bt_modify_name` writes directly to the BT stack (and can persist to VM via `lmp_hci_write_local_name`), even subsequent reboots could continue showing "Buddie" from the VM-cached value until a full CFG+VM erase was performed.

---

## Fix Applied

`apps/earphone/app_main.c` — removed the hardcoded call:

```c
// BEFORE
bt_modify_name("Buddie");
if (!pca_task_is_open) {

// AFTER
if (!pca_task_is_open) {
```

The BT name is now set exclusively from `cfg_tool.bin` via `cfg_file_parse` during earphone initialization.

---

## Files Changed

| File | Change |
|------|--------|
| `apps/earphone/app_main.c` | Removed `bt_modify_name("Buddie")` call at line 318 |

---

## Related: Stale Name in VM

Even after this fix, if "Buddie" was previously written into VM by the old firmware, the VM copy will take precedence on first boot until it is cleared. Use the identity-clean flash script to force full erase on the next flash:

```
cpu\br28\tools\download\earphone\download_app_ota_identity_clean.bat
```

Script uses `-format all` which erases CFG and VM regions so the device reads a fresh name from `cfg_tool.bin` on first boot.

---

## After Flashing

1. Forget old pairing on phone/PC — Bluetooth host OS aggressively caches device names.
2. Rescan — device name should now match what was set in the Config GUI.

---

## Note for Future Customization

If you need to set a fallback default name in firmware (for boards where `cfg_tool.bin` is absent or blank), the correct place is inside `cfg_file_parse` in `apps/earphone/user_cfg.c`, using the existing `ret < 0` branch:

```c
ret = syscfg_read(CFG_BT_NAME, tmp, 32);
if (ret < 0) {
    // safe place to set a firmware default name
    memcpy(bt_cfg.edr_name, "MyDevice", 8);
}
```

Do **not** call `bt_modify_name()` after app startup as it bypasses the config system.
