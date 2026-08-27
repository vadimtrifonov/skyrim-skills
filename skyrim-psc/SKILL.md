---
name: skyrim-psc
description: Compile Skyrim Papyrus PSC files to PEX with Caprica.
---

# Skyrim PSC

Use this skill directory as the working directory.

## Prepare

```bash
mise trust mise.toml
mise install
```

## Source imports

Find only the source directories required by the input PSC and active runtime APIs.
Common layouts are `Scripts/Source` and `Source/Scripts`.

Use this import precedence:

1. Input PSC directory (automatic).
2. Active API override sources.
3. Matching SKSE64 or SKSEVR sources.
4. Referenced mod API sources.
5. Referenced Creation content sources.
6. Skyrim SE 1.5.97 Creation Kit sources (automatic).

The helper adds items 1 and 6.
Pass the applicable items 2–5 with `-i`.
When PSC names collide, put the provider whose declarations match the target runtime first.
Caprica keeps the first PSC when names collide.
Order has no effect on unique PSC names.
Keep each source provider in a separate directory.

Match SKSE64 or SKSEVR sources to the target executable, not to master-file versions.
Script-extender sources supply declarations for extender APIs and selected core scripts.
The automatic source set supplies the remaining vanilla declarations.
For Skyrim VR, use VR-compatible sources for referenced native mod APIs.
Put active API override sources such as Skyrim VR ESL Support before the matching script-extender sources.

## Compile

```bash
mise exec -- python scripts/compile_psc.py \
  "<script.psc>" \
  -i "<highest-priority-source-directory>" \
  -i "<next-source-directory>" \
  -o "<output-directory>"
```

Use the printed import order to confirm that each selected override precedes the source that it replaces.
The helper emits one PEX for the input PSC. It does not update plugin VMAD data.
Imported PSC files supply declarations only. Caprica does not copy their function bodies into the output PEX.

## References

- [Caprica Limitations](references/caprica-limitations.md) - Compound array-element assignments, access to auto-properties declared by parent scripts, and PEX hash differences.
