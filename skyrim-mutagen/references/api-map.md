# Mutagen API Entry Points

The canonical documentation is under `tools/Mutagen/docs`. Start with `Big-Cheat-Sheet.md`, then use these entry points for the task at hand.

| Task | Entry points | Why they matter | Documentation |
| --- | --- | --- | --- |
| Read one plugin | `SkyrimMod.Create`, `FromPath`, `Construct`, `Mutable` | Read-only construction creates a lazy overlay; `Mutable` imports the complete plugin for editing. | `plugins/Importing.md` |
| Read only header masters | `MasterReferenceCollection.FromPath` | Retrieves the current ModKey and master list without importing the complete plugin. | `Big-Cheat-Sheet.md` |
| Build a controlled environment | `GameEnvironment.Typical.Builder`, `WithTargetDataFolder`, `WithLoadOrder`, `TransformLoadOrderListings`, `WithOutputMod` | Supplies explicit Data, load-order, filtering, and output-mod context. | `environment/Environment-Construction.md` |
| Enumerate plugin records | `EnumerateMajorRecords`, `EnumerateMajorRecordContexts` | Walks top-level and nested major records without selecting every record group separately. | Generated `SkyrimMod_Generated.cs` |
| Select active definitions | `WinningOverrides`, `WinningContextOverrides` | Returns one winner per FormKey; context variants retain the provider and nested-record path. | `loadorder/Winning-Overrides.md`, `linkcache/ModContexts.md` |
| Resolve links and chains | `ToImmutableLinkCache`, `ToMutableLinkCache`, `TryResolve`, `Resolve`, `ResolveAll`, `ResolveAllContexts` | Resolves FormKeys and FormLinks against listed mods or retrieves a selected override chain. | `linkcache/index.md`, `linkcache/Record-Resolves.md`, `linkcache/Previous-Override-Iteration.md` |
| Create or copy records | Group `AddNew`, `DuplicateInAsNewRecord`, `Duplicate`, `GetOrAddAsOverride`, `DeepCopy` | Distinguishes new FormKeys, duplicates, and overrides that preserve the source FormKey. | `plugins/Create,-Duplicate,-and-Override.md` |
| Keep generated FormKeys stable | `TextFileFormKeyAllocator`, `TextFileSharedFormKeyAllocator` | Persists EditorID-to-FormID assignments between runs. This API is marked experimental. | `plugins/FormKey-Allocation-and-Persistence.md` |
| Write a plugin | `BeginWrite`, `ToPath`, `WithLoadOrder`, `WithExtraIncludedMasters`, `WithExplicitOverridingMasterList` | Controls destination, required-master discovery, and master ordering. | `plugins/Exporting.md` |
| Inspect record equality | `Equals`, `GetEqualsMask`, generated `TranslationMask` classes | Can identify equal fields or restrict equality to selected fields. Mutagen marks this functionality as work in progress. | `plugins/Equality-Checks.md`, `plugins/Translation-Masks.md` |
| Enumerate record asset paths | `EnumerateAllAssetLinks`, `EnumerateListedAssetLinks`, `AssetLinkQuery`, `CreateImmutableAssetLinkCache` | Exposes listed, inferred, and FormLink-resolved assets as Data-relative paths. | `plugins/AssetLink.md` |
| Read archive members | `Archive.CreateReader`, `IArchiveReader.Files`, `IArchiveFile.GetBytes`, `GetSpan`, `AsStream` | Enumerates BSA or BA2 contents and reads selected members without unpacking the complete archive. | `Archives.md` |

## Skyrim record source

Generated record declarations are under:

```text
tools/Mutagen/Mutagen.Bethesda.Skyrim/Records
```

Search `<RecordName>_Generated.cs` for exact interfaces, property types, and concrete variants. Useful starting points include:

- `Records/Major Records/GlobalShort_Generated.cs` and `GlobalFloat_Generated.cs` for GLOB variants;
- `Interfaces/Aspect/IHaveVirtualMachineAdapter.cs`, `Records/Common Subrecords/AVirtualMachineAdapter.cs`, and `ScriptEntry_Generated.cs` for VMAD;
- `Records/Major Records/Cell_Generated.cs`, `Worldspace_Generated.cs`, and `Extensions/*ContextExt.cs` for nested records;
- projects ending in `.UnitTests` for behavior not specified by the documentation.

When an interface accepts several concrete implementations, inspect those implementations before constructing a replacement value. Equal displayed values can have different binary types.
