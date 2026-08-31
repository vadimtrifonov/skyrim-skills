[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string] $TaskName = 'scratch'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

try {
    if ([string]::IsNullOrWhiteSpace($env:MUTAGEN_ROOT)) {
        throw 'MUTAGEN_ROOT is unset; run this command through mise'
    }

    $mutagenProject = Join-Path $env:MUTAGEN_ROOT 'Mutagen.Bethesda.Skyrim/Mutagen.Bethesda.Skyrim.csproj'
    if (-not (Test-Path -LiteralPath $mutagenProject -PathType Leaf)) {
        throw "Mutagen is not set up; run 'mise run setup' in the skill directory"
    }

    $slug = [regex]::Replace($TaskName.Trim().ToLowerInvariant(), '[^a-z0-9]+', '-').Trim('-')
    if ($slug.Length -gt 48) {
        $slug = $slug.Substring(0, 48).TrimEnd('-')
    }
    if ([string]::IsNullOrEmpty($slug)) {
        $slug = 'scratch'
    }

    $suffix = [Guid]::NewGuid().ToString('N').Substring(0, 12)
    $destination = Join-Path ([IO.Path]::GetTempPath()) "skyrim-mutagen-$slug-$suffix"
    [IO.Directory]::CreateDirectory($destination) | Out-Null

    $templateRoot = Join-Path (Split-Path -Parent $PSScriptRoot) 'templates'
    try {
        foreach ($name in 'Scratch.csproj', 'Program.cs') {
            $source = Join-Path $templateRoot $name
            if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
                throw "Template does not exist: $source"
            }
            Copy-Item -LiteralPath $source -Destination (Join-Path $destination $name)
        }
    }
    catch {
        Remove-Item -LiteralPath $destination -Recurse -Force -ErrorAction SilentlyContinue
        throw
    }

    Write-Output ([IO.Path]::GetFullPath($destination))
}
catch {
    [Console]::Error.WriteLine("ERROR: $($_.Exception.Message)")
    exit 2
}
