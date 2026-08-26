---
name: skyrim-record-chain
description: Query active Skyrim record-definition chains by FormKey from a SE/AE or VR load order, including MO2 profiles.
---

# Skyrim Record Chain

Use this skill directory as the working directory.

## Setup

```bash
mise trust mise.toml
mise install
```

## Query inputs

Each query supplies an explicit game, Data folder, `plugins.txt`, and FormKey input.

`--game` accepts `SkyrimSE` or `SkyrimVR`. `SkyrimSE` covers Special Edition and Anniversary Edition.
FormKeys use the form `03372B:Skyrim.esm`.

`<FormKey-input>` in the command templates means exactly one of:

- `"<FormKey>"`
- `--formkeys-from "<path|->"` for one FormKey per line

`-` reads the CLI process's standard input. Empty, invalid, and duplicate batch entries are errors.

The resolved active order combines Skyrim's implicit plugins, installed entries from `Skyrim.ccc` beside the Data folder, and enabled non-ghosted entries from `plugins.txt`.
A missing active plugin or required master is an error.

## MO2 query

MO2 exposes the selected profile's virtualized Data view to processes that it launches and their descendants.

`ModOrganizer.exe run` returns only MO2's completion status. A command wrapper writes the CLI JSONL, diagnostics, and exit code to files:

```batch
@echo off
cd /d "<skill-directory>"

mise exec -- skyrim-record-chain.exe ^
  --game <SkyrimSE|SkyrimVR> ^
  --data-folder "<game Data>" ^
  --load-order "<MO2>\profiles\<profile>\plugins.txt" ^
  <FormKey-input> > "<chain.jsonl>" 2> "<chain.err>"

set "code=%ERRORLEVEL%"
> "<chain.exit>" echo %code%
exit /b %code%
```

Launch the wrapper under the selected profile:

```powershell
& "<MO2>\ModOrganizer.exe" `
  -p "<profile>" run `
  -a '/d /c ""<runner.cmd>""' `
  -c "<runner-directory>" `
  "$env:ComSpec"
```

`chain.exit` is written last and contains the CLI exit code.

## Physical Data query

When all active plugin files are visible without MO2, run the CLI directly:

```powershell
mise exec -- skyrim-record-chain.exe `
  --game <SkyrimSE|SkyrimVR> `
  --data-folder "<Data>" `
  --load-order "<plugins.txt>" `
  <FormKey-input>
```

## Output

The command writes one compact JSON object per line. For batch input, FormKeys follow input order and each chain is contiguous.
Rows in each chain follow active load order from origin to winner.

Each row contains:

- Record identity: `formKey`, `type`, `editorId`
- Provider identity: `loadOrderIndex`, `plugin`, `pluginPath`
- Header state: `majorRecordFlagsRaw`, `deleted`, `partial`
- Chain position: `origin`, `winner`

Field semantics:

- `loadOrderIndex` is zero-based in the resolved active order
- `majorRecordFlagsRaw` is an unsigned 32-bit value that contains all record-header flags
- `origin` marks the first resolved definition, whose provider can differ from the FormKey's ModKey for an injected record
- `winner` marks the final definition
- `partial` decodes the Partial Form bit for cells, dialog topics, and worldspaces

Under MO2, `pluginPath` refers to the virtual Data path used by that profile.

Deleted and partial definitions remain in the chain.

Diagnostics use standard error. An error returns a nonzero exit code and leaves standard output empty, including for a partly valid batch.
