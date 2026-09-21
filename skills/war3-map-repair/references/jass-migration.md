# JASS compatibility: diagnosis and verified migration

## Why this is separate from SLK repair

In the HLWL A4.6 case, both the original map and the SLK-only candidate were rejected by the game. The actual client log reported five return-type errors and two `GetSpellTargetX/Y` name collisions. Reading the MPQ or finding old SLK tables did not establish the cause of that rejection.

Always inspect the actual game log for the failing map. `repair_jass.py MAP.w3x` reports suspicious helpers and known script fingerprints, but is not a complete JASS compiler. A warning is not proof that the current client rejects the script. The scanner accepts either `war3map.j` or `scripts/war3map.j`, refuses ambiguous dual entries, and never writes in audit mode.

## Supported repair profile

`hlwl-a4.6` matches the exact original JASS SHA-256, whether the surrounding map has already received SLK repair or not. It refuses unknown or already-repaired script content. It does not identify support from the filename alone. This conservative profile is deliberately not an automatic migration for all YDWE maps.

```powershell
# Same Windows / StormLib setup as the SLK tool
python skills/war3-map-repair/scripts/repair_jass.py "map.w3x"
python skills/war3-map-repair/scripts/repair_jass.py "map.slk.w3x" --profile hlwl-a4.6 --output "map.jass.w3x"
# Optional compiler check before creating output; supply all three arguments
python skills/war3-map-repair/scripts/repair_jass.py "map.slk.w3x" --profile hlwl-a4.6 --output "map.checked.w3x" --pjass "C:\Tools\pjass.exe" --common "C:\Tools\common.j" --blizzard "C:\Tools\blizzard.j"
```

The JASS tool changes only the script entry. It does not run SLK repair implicitly. To reproduce the successful historical combined candidate, first run `repair_map.py --migrate-models --extend-levels`, then run the JASS profile on that candidate. Neither step overwrites its input or an existing output.

The profile:

- Replaces two handle-to-integer return-bug helpers with `GetHandleId`.
- Replaces integer-to-group/location/rect casts with matching typed hashtable loads.
- Migrates 47 matching stores to typed hashtable saves while retaining ordinary gamecache integer counters.
- Extends 31 mission cleanup calls and the full-cache cleanup to clear typed storage too.
- Initializes the hashtable with the existing cache initialization.
- Renames the map's two coordinate helpers and identifier references, preserving their implementation and string/comment contents.

All typed storage parents in this verified script originate from `I2S(integer)`, so `S2I` preserves those keys. Child keys use `StringHash`. These assumptions must be reviewed before adding any other profile; they are not general truths about arbitrary gamecache usage. There are no new balance, drop-rate, or gameplay-trigger removals.

## Validation and limits

Regression reproduced the exact previously tested C map SHA-256 `6429e211b469f53a8a418e674fb31834b0e708c15594a25ed19fb15d73a6310e`; 74 non-script resource blocks stayed identical to the SLK-only input. The user confirmed the C map could run. This is not a complete ability-by-ability or full-playthrough test.

[Official pjass](https://github.com/lep/pjass) with [YDWE's standard JASS 1.24 libraries](https://github.com/actboy168/YDWE/tree/master/Development/Component/compiler/jass/24) reproduced 7 errors in the original and 0 in the migrated script. These are not the exact Reforged 3.0 client libraries. Optional compiler output is supplementary; actual client loading and gameplay remain necessary. No compiler binaries, game libraries, or map scripts are distributed here.

The tool records source/output hashes, compiler/library hashes when supplied, migration counts, archive verification and runtime status. An unrecognized fingerprint produces no candidate. Extending support requires a new reviewed profile, paired store/load/cleanup analysis, a positive regression and rejection tests. Do not remove the fingerprint gate to force an unknown map through this profile.
