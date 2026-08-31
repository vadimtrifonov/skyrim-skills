[CmdletBinding()]
param(
    [switch] $Integration
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$writeSmoke = Join-Path $PSScriptRoot 'fixtures/WriteSmoke.cs'
$mise = (Get-Command mise -ErrorAction Stop).Source

function Assert-True {
    param(
        [bool] $Condition,
        [string] $Message
    )

    if (-not $Condition) {
        throw $Message
    }
}

function Invoke-Checked {
    param(
        [string] $FilePath,
        [string[]] $ArgumentList = @(),
        [int] $ExpectedExitCode = 0
    )

    $output = & $FilePath @ArgumentList 2>&1 | Out-String
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne $ExpectedExitCode) {
        throw "Command failed with exit code $exitCode (expected $ExpectedExitCode): $FilePath $($ArgumentList -join ' ')`n$output"
    }
    return $output
}

function New-TestScratch {
    param([string] $TaskName)

    $output = Invoke-Checked -FilePath $mise -ArgumentList @(
        'run',
        'scratch',
        $TaskName
    )
    return [IO.Path]::GetFullPath($output.Trim())
}

$cleanup = [Collections.Generic.List[string]]::new()
try {
    $scaffold = New-TestScratch -TaskName 'Record Audit'
    $cleanup.Add($scaffold)

    $tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $scaffoldParent = (Split-Path -Parent $scaffold).TrimEnd([IO.Path]::DirectorySeparatorChar)
    Assert-True ($scaffoldParent -eq $tempRoot) 'Scratch project was not created directly under the system temp directory'
    Assert-True ((Split-Path -Leaf $scaffold).StartsWith('skyrim-mutagen-record-audit-')) 'Scratch directory name does not contain the task slug'

    $actualNames = @(
        Get-ChildItem -LiteralPath $scaffold -File |
            Sort-Object Name |
            Select-Object -ExpandProperty Name
    )
    Assert-True (($actualNames -join ',') -eq 'Program.cs,Scratch.csproj') "Unexpected scaffold files: $($actualNames -join ', ')"
    Write-Output 'PASS: scratch scaffold'

    if ($Integration) {
        $dotnet = (Get-Command dotnet -ErrorAction Stop).Source
        $work = New-TestScratch -TaskName 'integration'
        $cleanup.Add($work)
        $project = Join-Path $work 'Scratch.csproj'

        Invoke-Checked -FilePath $dotnet -ArgumentList @(
            'build', $project, '--nologo', '-clp:ErrorsOnly'
        ) | Out-Null
        $usage = Invoke-Checked -FilePath $dotnet -ExpectedExitCode 2 -ArgumentList @(
            'run', '--no-build', '--project', $project
        )
        Assert-True ($usage -match 'Usage: Scratch') 'Inspection template did not print its usage message'

        $program = Join-Path $work 'Program.cs'
        [IO.File]::WriteAllText($program, [IO.File]::ReadAllText($writeSmoke))
        Invoke-Checked -FilePath $dotnet -ArgumentList @(
            'build', $project, '--nologo', '-clp:ErrorsOnly'
        ) | Out-Null
        $writeResult = Invoke-Checked -FilePath $dotnet -ArgumentList @(
            'run', '--no-build', '--project', $project, '--', $work
        )
        Assert-True ($writeResult -match 'write smoke passed') 'Write smoke test did not report success'
        Write-Output 'PASS: inspection and write workflows'
    }
}
finally {
    foreach ($path in $cleanup) {
        Remove-Item -LiteralPath $path -Recurse -Force -ErrorAction SilentlyContinue
    }
}
