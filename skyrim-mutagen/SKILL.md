---
name: skyrim-mutagen
description: Create temporary C# projects against the current Mutagen source. Use for Skyrim record inspection, synthetic plugin fixtures, and plugin generation.
---

# Skyrim Mutagen

Use this skill directory as the working directory.

## Setup

```powershell
mise trust mise.toml
mise install
mise run setup
```

Setup clones or updates Mutagen's `dev` branch under `tools/Mutagen`.
Mise exposes that checkout as `MUTAGEN_ROOT`.

## Create a scratch project

```powershell
$work = (mise run scratch "<task-name>").Trim()
```

The command prints the path of a new directory under `%TEMP%`.

The directory contains:

- `Scratch.csproj`, which references `$(MUTAGEN_ROOT)/Mutagen.Bethesda.Skyrim/Mutagen.Bethesda.Skyrim.csproj`;
- `Program.cs`, a working read-only plugin inspection example.

Build and run the project through this skill's mise environment:

```powershell
mise exec -- dotnet build "$work\Scratch.csproj" --nologo "-clp:ErrorsOnly"
mise exec -- dotnet run --no-build --project "$work\Scratch.csproj" -- SkyrimVR "<plugin-path>"
```

The example accepts `SkyrimSE` or `SkyrimVR` followed by one plugin path.

Run builds sequentially.
Project references share `tools/Mutagen` build outputs even though the scratch source is under `%TEMP%`; concurrent builds can lock those outputs.

## Input context

Select the release explicitly: `SkyrimVR` for Skyrim VR and `SkyrimSE` for Special Edition.

`GameEnvironment.Typical` reads the standard game installation and load-order locations.
For an MO2 profile, supply its ordered active listings and resolved physical plugin paths explicitly.
Do not recursively scan the `mods` directory and accept the first matching filename; directory enumeration is not MO2 priority order.

For localized plugins, select the target language and resolve the winning strings independently of the plugin path.
In MO2, the plugin and strings may have different providers.

## References

- [Common patterns](references/workflows.md): import, localized strings, record identity, explicit load orders, resolution, overrides, serialization checks, and equality.
- [API entry points](references/api-map.md): task-oriented links to Mutagen documentation and generated source.
