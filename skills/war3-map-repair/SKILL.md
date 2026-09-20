---
name: war3-map-repair
description: Diagnose Warcraft III custom maps that fail after a client update, especially embedded legacy SLK overrides; perform backed-up, minimal compatibility repairs and separate crash, script, and minimap issues.
---

# Warcraft III map compatibility repair

Use the user's original map or identified working backup. Distinguish a compatibility repair from gameplay changes; do not change loot, triggers, or balance as an incidental repair.

Read [the case study](references/case-study.md) before selecting a repair. This is evidence from two maps, not a universal Warcraft RPG fix. The cases were reported after Warcraft III: Reforged patch 3.0, released alongside Forsaken Kingdom. Record the actual executable build separately when available; the exact affected build and causal engine change were not isolated.

## Workflow

1. Record symptoms, client build, render mode, map hash, and whether the failure happens before loading, during initialization, or in play. Keep the original immutable. Do not start from a previous unsuccessful modification when a clean backup exists.
2. Inspect the MPQ and embedded `Units\UnitUI.slk`, `Units\ItemData.slk`, skin files and `Units\AbilityData.slk`. Compare against a working map or this client's schema. Read-only audit is the default:
   `python scripts/repair_map.py MAP.w3x`
3. If the evidence matches legacy model overrides, generate a separate candidate:
   `python scripts/repair_map.py MAP.w3x --output MAP.compat.w3x --migrate-models`
   Existing skin files require a reviewed merge; the tool refuses to overwrite them. Do not delete custom models or replace the entire object database.
4. Level 5/6 ability column filling is a separate, opt-in workaround: add `--extend-levels`. It copies level 4 values and can affect abilities whose intended upper levels differ. Use only when schema comparison and intended behavior justify it. Two simultaneous changes do not prove which one caused the crash.
5. The tool verifies changed entry read-back, original block bytes outside the allowlist, unchanged script/terrain/object data, and a source hash. Inspect the report. Test candidate in the actual game: loading, visible units/items, initialization, abilities, minimap, and a short play session. A successful archive read is not an in-game test. Keep runtime status “unverified” until observed.
6. Only install when requested or implied by the repair task. Preserve a separate backup and clear original/candidate filenames. Report what changed, what was tested, remaining defects, and rollback path.

## Important distinctions

- An embedded table schema mismatch is not evidence of a broken JASS native/API. Investigate JASS or extension natives only with supporting traces or script evidence.
- Do not disable initialization, triggers, or model creation merely to make loading appear successful.
- A black minimap after loading is a separate symptom. Compare `war3mapMap.blp`, terrain, visibility/fog logic and renderer behavior. An unchanged image does not prove the client displays it correctly. Do not claim the minimap is fixed by a crash fix.
- Map protection, corrupt archives, third-party platform natives, malformed scripts and renderer/model problems need their own diagnosis. Stop this automated path when the signature does not match.

## Requirements

Windows, Python 3.10+, `mpyq`, and a matching-architecture StormLib DLL obtained from [official upstream](https://github.com/ladislav-zezula/StormLib). Set `STORMLIB_DLL` to its absolute path. Scripts do not download or bundle binaries. The skill folder is self-contained; `scripts/requirements.txt` declares the Python dependency.
