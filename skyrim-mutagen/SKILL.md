---
name: skyrim-mutagen
description: Create temporary C# projects against the current Mutagen source. Use for custom Skyrim plugin or archive analysis and plugin generation.
---

# Skyrim Mutagen

Use this skill directory as the working directory.

## Setup

```powershell
mise trust mise.toml
mise install
mise run setup
```

Setup clones or updates Mutagen's `dev` branch under `tools/Mutagen`. Mise exposes that checkout as `MUTAGEN_ROOT`.

## Create a scratch project

```powershell
$work = (mise exec -- python scripts/new_scratch.py "<task-name>").Trim()
```

The command prints the path of a new directory under `%TEMP%`. The directory contains:

- `Scratch.csproj`, which references `$(MUTAGEN_ROOT)/Mutagen.Bethesda.Skyrim/Mutagen.Bethesda.Skyrim.csproj`;
- `Program.cs`, a working read-only plugin inspection example.

Build or run the project through this skill's mise environment:

```powershell
mise exec -- dotnet build "$work\Scratch.csproj"
mise exec -- dotnet run --project "$work\Scratch.csproj" -- SkyrimVR "<plugin-path>"
```

The example accepts `SkyrimSE` or `SkyrimVR` followed by one plugin path.
Edit `Program.cs` for the required diagnostic or generator.

## Input context

Select the Mutagen game release explicitly.
Use `SkyrimVR` when modeling the VR runtime and `SkyrimSE` when modeling Special Edition.

`GameEnvironment.Typical` reads the standard game installation and load-order locations.
For an MO2 profile, supply its active listings and physical plugin paths explicitly.

## References

- [Common patterns](references/workflows.md): plugin import, FormKeys, link caches, overrides, output, and archive members.
- [API entry points](references/api-map.md): selected Mutagen APIs, documentation, and generated source locations.
