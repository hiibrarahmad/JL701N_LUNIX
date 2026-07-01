---
tags: [factory, flashing, provisioning, tws, mac]
date: 2026-04-28
status: Process note
---

# Factory Flash Workflow - Manual Pair Mapping

## Goal

Program each bud with:

- its own unique local EDR MAC
- its designated sibling EDR MAC

No automatic firmware MAC derivation is used in this workflow.

---

## Per-Unit Steps

1. Open [[MAC ADDRESS MASTER LIST - 10 Buds 5 Pairs]].
2. Pick the target row by Unit ID.
3. In config tool, set Local EDR MAC from that row.
4. Set sibling remote address to that row Sibling EDR MAC.
5. Build firmware image with row Firmware Profile ID naming.
6. Flash target unit and mark status as Flashed.

---

## Per-Pair Validation Steps

1. Power only the two units of the same Pair ID.
2. Confirm they form TWS correctly.
3. Start audio playback and verify both channels.
4. Put in case, remove, and verify reconnect.
5. Power adjacent pair and re-check no cross-pair connection.
6. Update status columns in master list.

---

## Failure Handling

If wrong pair is formed:

1. Verify both units were flashed with correct row.
2. Re-check Local EDR MAC and Sibling EDR MAC values.
3. Clear stale pair info on both units if needed.
4. Reflash both buds with correct pair rows.

If one unit replaced:

1. Assign new unique local MAC for replacement.
2. Update sibling mapping on both buds in that pair.
3. Reflash both pair members to keep symmetric mapping.

---

## Release Sign-Off

Before batch sign-off, all rows should include:

- Programmed By
- Program Date
- Verification Status = Reconnect Pass
- Notes for any rework history
