# Common Mutagen Patterns

## Read a plugin

A read-only overlay parses records lazily and keeps the input open:

```csharp
using Mutagen.Bethesda.Skyrim;

using var mod = SkyrimMod.Create(SkyrimRelease.SkyrimVR)
    .FromPath(pluginPath)
    .Construct();
```

Add `.Mutable()` before `.Construct()` only when modifying the imported plugin. Mutable import parses the complete file.

## Use stable record identities

```csharp
using Mutagen.Bethesda.Plugins;

var modKey = ModKey.FromFileName("Skyrim.esm");
var formKey = FormKey.Factory("03372B:Skyrim.esm");
```

A FormKey contains the originating ModKey and local FormID. It does not contain a runtime load-order index.

Fields with binary variants require the matching concrete type. For example, a Skyrim GLOB can be `GlobalShort`, `GlobalFloat`, or another variant even when its displayed value is numerically equal.

## Resolve records

Create an immutable link cache when its backing mods will not gain or lose records:

```csharp
var linkCache = listedMods.ToImmutableLinkCache();
```

- `TryResolve` reports an unresolved optional link without throwing.
- `Resolve` throws when the record is absent.
- `ResolveAllContexts` returns the selected record's definitions and their provider ModKeys.
- Context APIs are required to override nested records such as cells and placed references.

Use a mutable link cache when adding or removing records from an output mod included in the cache.

## Create an override

```csharp
var output = new SkyrimMod(
    ModKey.FromFileName("My Patch.esp"),
    SkyrimRelease.SkyrimVR);

var patchedNpc = output.Npcs.GetOrAddAsOverride(sourceNpc);
patchedNpc.Name = "New Name";
```

`GetOrAddAsOverride` preserves the source FormKey. Duplication creates a new FormKey instead.

Write with the load order that should determine master ordering:

```csharp
await output.BeginWrite
    .ToPath(outputPath)
    .WithLoadOrder(loadOrder)
    .WriteAsync();
```

Mutagen derives required masters from emitted records unless the write builder is configured otherwise.

## Read selected archive members

```csharp
using Mutagen.Bethesda;
using Mutagen.Bethesda.Archives;

var archive = Archive.CreateReader(GameRelease.SkyrimSE, archivePath);
var files = archive.Files.ToDictionary(
    file => file.Path.Replace('\\', '/'),
    StringComparer.OrdinalIgnoreCase);

var member = files[requestedPath.Replace('\\', '/')];
using var input = member.AsStream();
using var output = File.Create(destinationPath);
await input.CopyToAsync(output);
```

Archive lookup scans the file index but decompresses only members whose data is read. Normalize separators and compare member paths case-insensitively. Reject ambiguous normalized paths before extraction.
