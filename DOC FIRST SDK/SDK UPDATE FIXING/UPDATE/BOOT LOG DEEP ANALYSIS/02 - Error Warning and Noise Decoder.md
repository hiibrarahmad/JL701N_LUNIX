# Error Warning and Noise Decoder

## 1) Real Errors in Your Log

### A) `wtgv2_dec err:64`

Observed:
- `[AUDIO_DECODER]wtgv2_dec err:64`

Meaning:
- Decoder for WTG/WTS prompt stream reached an unexpected decode state.
- Usually non-fatal for system operation; affects prompt/tone playback robustness.

Common causes:
- Prompt file format mismatch
- Corrupted prompt blob/file
- Interrupted prompt chain while mode switching

Impact:
- Low to medium. Bluetooth and TWS can still run.

Action:
- Check tone assets and packaging consistency.
- Confirm sample rate/format expected by current decoder build.

---

### B) `Open [/config.dat] Fail! (>_<)` and `file open fail`

Observed:
- `[SDFILE]Open ... [/config.dat] Fail! (>_<)`
- `file open fail`

Meaning:
- Runtime attempts to open optional configuration data file and cannot find it.

Impact:
- Usually low if fallback defaults are available.
- If RCSP/custom app features require this file, feature behavior may degrade.

Action:
- Ensure config package includes `config.dat` when those features are required.
- If intentionally absent, this can be accepted as informational noise.

---

### C) `lmp_super_timeout` then detach reason `8`

Observed:
- `[LMP]lmp_super_timeout`
- `do_detach : 8,30`
- `ERROR_CODE_CONNECTION_TIMEOUT`

Meaning:
- Link supervision timer expired (temporary RF/peer response issue).

Impact:
- Medium. Link dropped and reconnect logic restarted.

Action:
- Verify peer availability and RF environment.
- Ensure target peer MAC/address set is correct.
- This happened before stable phone attach in your capture.

---

### D) Detach reason `19`

Observed:
- `LMP_DETACH: 19`
- `bt_hci_event_handler reason ... 13`

Meaning:
- Remote/user initiated disconnection path in protocol state machine.

Impact:
- Medium but often expected during negotiation changes.

Action:
- If frequent in steady state, inspect role switch, scan transitions, and policy.

## 2) Not-Errors (Often Misread as Failures)

### `aec cfg read err ret: -251, ... use default value`

Meaning:
- AEC profile record not present in VM/config section.
- Firmware falls back to default mic/dac gains.

Impact:
- Not a boot failure. Audio still works with defaults.

### `err priority 7 : priority 6 is reserved fot GIEMASK`

Meaning:
- Scheduler warning from task creation attempt with reserved priority neighbor.
- Idle task still created and system continues.

Impact:
- Usually non-fatal in this SDK logging style.

### `not LMP_SETUP_COMPLET`

Meaning:
- Intermediate handshake stage before full setup complete.
- Followed by successful setup lines in your log.

Impact:
- Informational during connection progression.

### Long `PPPP`, `CCCC`, `www`, `I`, `%@` bursts

Meaning:
- Mixed UART stream artifacts/debug chars from concurrent modules or binary-ish debug tags.
- Not protocol messages by themselves.

Impact:
- Noise unless correlated with a nearby explicit error line.

## 3) Address and Provisioning Specific Warnings

### `tws pair code config: FF FF`

Meaning:
- Pair code read from storage was 0xFFFF (uninitialized/invalid for your intended setup).

Expected (your design):
- `0x6688` for Pair 1.

### Runtime EDR MAC `BB 0A 2C 77 5B 37`

Meaning:
- Random/fallback MAC path active in this run.

Expected (your design):
- Left: `3C:00:0A:7E:1A:00`
- Right: `3C:00:0A:7E:1A:01`

## 4) Severity Summary

- High priority to fix:
  - Provisioning mismatch (random MAC, pair code FF FF)
- Medium priority:
  - Intermittent supervision timeout/reconnect loops
- Low priority:
  - Missing `config.dat` if optional in your deployment
  - Decoder `err:64` if only prompt playback is affected

## 5) Practical Verification After Next Flash

After flashing Left/Right images, confirm these log signatures:
- `Provisioning Pair 1 - LEFT BUD (B01)` on left build
- `Provisioning Pair 1 - RIGHT BUD (B02)` on right build
- `CFG_BT_MAC_ADDR ... 3C:00:0A:7E:1A:00` (left) / `...01` (right)
- `tws pair code config` prints bytes corresponding to `0x6688`, not `FF FF`
- `mac:` hexdump matches provisioned value
