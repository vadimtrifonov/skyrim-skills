---
name: skyrim-spriggit
description: Serialize Skyrim plugins (ESP/ESL/ESM) to editable Spriggit JSON trees and rebuild plugins from those trees. Use to list all major records as normalized JSONL or retrieve one complete record by FormKey.
---

# Skyrim Spriggit

Use this skill directory as the working directory.

## Setup

```bash
mise trust mise.toml
mise install
```

## Serialize

Use a clean, dedicated output directory; `<ModName>.spriggit` is the preferred name.

```bash
mise exec -- Spriggit.CLI.exe serialize --InputPath "<plugin.esp>" --OutputPath "<ModName>.spriggit" --GameRelease <SkyrimSE|SkyrimVR> --PackageName Spriggit.Json --PackageVersion <version>
```

## List records

```bash
mise exec -- python scripts/list_records.py "<ModName>.spriggit" > "<ModName>.records.jsonl"
```

The output includes records embedded in cells and worldspaces, such as placed references, landscapes, and navigation meshes.

Each line contains these fields:

- `type`
- `formKey`
- `editorId`
- `kind`: `new` or `override`
- `deleted`

The helper does not load masters or identify conflicts.

## Get record

```bash
mise exec -- python scripts/get_record.py "<ModName>.spriggit" "<FormKey>"
```

The output contains the source file, the path inside that file, and the complete record object. The lookup matches a record's own `FormKey`, not references to that FormKey.

## Deserialize

Package and game metadata are read from the serialized tree.

```bash
mise exec -- Spriggit.CLI.exe deserialize --InputPath "<ModName>.spriggit" --OutputPath "<plugin.esp>"
```
