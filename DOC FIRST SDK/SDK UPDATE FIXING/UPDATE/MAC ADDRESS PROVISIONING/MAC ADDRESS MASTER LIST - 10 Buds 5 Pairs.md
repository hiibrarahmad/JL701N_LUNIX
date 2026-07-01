---
tags: [mac, tws, provisioning, factory, identity]
date: 2026-04-28
status: Manual provisioning list
---

# MAC Address Master List - 10 Buds 5 Pairs

## Purpose

This document defines a fixed, manual MAC allocation plan for 10 earbuds (5 TWS pairs), with explicit local and sibling address mapping.

Key rule:

- Each bud has a unique local EDR MAC.
- Each bud stores only its designated sibling EDR MAC.
- Left and right in the same pair must not share the same local MAC.

---

## Base Address

- Base EDR MAC: 3C:00:0A:7E:1A:00
- Allocation method: increment last byte by +1 per bud

---

## Master Provisioning Table

| Pair ID | Bud Role | Unit ID | Firmware Profile ID | Local EDR MAC     | Sibling EDR MAC (write to CFG_TWS_REMOTE_ADDR) | Recommended BLE MAC | Pair Label | Flash Order | Programmed By | Program Date | Verification Status | Notes |
| ------- | -------- | ------- | ------------------- | ----------------- | ---------------------------------------------- | ------------------- | ---------- | ----------- | ------------- | ------------ | ------------------- | ----- |
| P01     | Left     | B01     | P01-L               | 3C:00:0A:7E:1A:00 | 3C:00:0A:7E:1A:01                              | 4C:00:0A:23:1F:12   | P01        | 1           |               |              | Pending             |       |
| P01     | Right    | B02     | P01-R               | 3C:00:0A:7E:1A:01 | 3C:00:0A:7E:1A:00                              | 4C:00:0A:23:1F:13   | P01        | 2           |               |              | Pending             |       |
| P02     | Left     | B03     | P02-L               | 3C:00:0A:7E:1A:02 | 3C:00:0A:7E:1A:03                              | 4C:00:0A:23:1F:14   | P02        | 3           |               |              | Pending             |       |
| P02     | Right    | B04     | P02-R               | 3C:00:0A:7E:1A:03 | 3C:00:0A:7E:1A:02                              | 4C:00:0A:23:1F:15   | P02        | 4           |               |              | Pending             |       |
| P03     | Left     | B05     | P03-L               | 3C:00:0A:7E:1A:04 | 3C:00:0A:7E:1A:05                              | 4C:00:0A:23:1F:16   | P03        | 5           |               |              | Pending             |       |
| P03     | Right    | B06     | P03-R               | 3C:00:0A:7E:1A:05 | 3C:00:0A:7E:1A:04                              | 4C:00:0A:23:1F:17   | P03        | 6           |               |              | Pending             |       |
| P04     | Left     | B07     | P04-L               | 3C:00:0A:7E:1A:06 | 3C:00:0A:7E:1A:07                              | 4C:00:0A:23:1F:18   | P04        | 7           |               |              | Pending             |       |
| P04     | Right    | B08     | P04-R               | 3C:00:0A:7E:1A:07 | 3C:00:0A:7E:1A:06                              | 4C:00:0A:23:1F:19   | P04        | 8           |               |              | Pending             |       |
| P05     | Left     | B09     | P05-L               | 3C:00:0A:7E:1A:08 | 3C:00:0A:7E:1A:09                              | 4C:00:0A:23:1F:1A   | P05        | 9           |               |              | Pending             |       |
| P05     | Right    | B10     | P05-R               | 3C:00:0A:7E:1A:09 | 3C:00:0A:7E:1A:08                              | 4C:00:0A:23:1F:1B   | P05        | 10          |               |              | Pending             |       |

---

## Required Config Fields Per Firmware Build

For each bud firmware image:

1. Set local EDR MAC to the row Local EDR MAC.
2. Set sibling address in VM to the row Sibling EDR MAC.
3. Keep pair code/device indicate consistent only within intended production batch rules.
4. Keep local MAC unique across all buds.

---

## Factory Check Columns Meaning

- Unit ID: physical serial slot in this batch list.
- Firmware Profile ID: image naming key to avoid left/right mix-up.
- Verification Status:
  - Pending
  - Flashed
  - Pair Pass
  - Audio Pass
  - Reconnect Pass
  - Rework

---

## Pair Validation Checklist

Run after flashing each pair:

1. Confirm both buds power on and discover only as intended identities.
2. Confirm pair forms with designated sibling (left with right of same Pair ID).
3. Confirm no cross-pair attach when all nearby units are powered.
4. Confirm music audio plays on both buds.
5. Confirm case out and reconnect behavior is stable.
6. Mark Verification Status columns.

---

## Notes

- This list is intentionally manual to avoid unintended auto-derivation in firmware.
- Do not assign the same local EDR MAC to both buds in one pair.
- If a unit is replaced, reserve old MAC and issue a new unique MAC to replacement, then update sibling mapping for that pair.
