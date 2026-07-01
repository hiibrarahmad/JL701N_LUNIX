# PC5 Pull-Up / Pull-Down Decision (JL7016G Hybrid)

## Your Question

Do you still need external pull-up or pull-down on PC5 after MAC implementation?

## Short Answer

For your current project policy and field behavior, **PC5 pull bias is required** for stable and predictable TWS side resolution.

MAC provisioning works, but it does not remove the need for a defined PC5 hardware state.

## Evidence from Current Board Config

From hybrid config:
- `TCFG_EXTERN_STORAGE_MODE_ENABLE = DISABLE_THIS_MOUDLE`
- `TCFG_EXTERN_STORAGE_MODE_BOAT_PL_PORT = IO_PORTC_05`

Interpretation:
- Even though extern storage mode is disabled in config, your real-world TWS behavior still depends on deterministic side/channel resolution and stable pin state.
- A floating or inconsistent PC5 level increases risk of non-seamless TWS transitions.

## Practical Hardware Recommendation

Even when a pin is feature-disabled, do not leave it floating.

Recommended:
1. Keep a weak default resistor (typically 47k-100k) to the safe inactive level for your hardware design intent.
2. Or configure firmware pull state explicitly in board init if the pin is truly unused.

## Which Direction (Up vs Down)?

Choose based on the inactive logic expected by your hardware option tied to PC5:
- If active state is high-enable, use pull-down for default inactive.
- If active state is low-enable, use pull-up for default inactive.

Project requirement update:
- Do not leave PC5 floating.
- Keep an explicit and validated bias strategy across the pair.

## Log-Based Observation

Your log does not show explicit PC5 fault signatures (no reset storm attributable to PC5 level, no storage-mode forced entry).

Latest integration notes classify PC5 bias as a required stability gate for this project.

## Final Decision for Current Project Stage

- PC5 pull bias is required and must be validated per bud.
- Keep deterministic left/right hardware bias policy in production checklist.
- Treat PC5 bias as mandatory for stable TWS behavior in this project.
