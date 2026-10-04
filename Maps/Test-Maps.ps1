[CmdletBinding()]
param([string]$EvidenceDirectory)

$ErrorActionPreference = 'Stop'
$gameRoot = Split-Path $PSScriptRoot -Parent
$smileRoot = [IO.Path]::GetFullPath((Join-Path $gameRoot '..\SMILE 2.0'))
$testRoot = Join-Path $gameRoot ('artifacts\map-checks-' + [Guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $testRoot
if (-not $EvidenceDirectory) { $EvidenceDirectory = Join-Path $testRoot 'evidence' }
$EvidenceDirectory = [IO.Path]::GetFullPath($EvidenceDirectory)
$null = New-Item -ItemType Directory -Path $EvidenceDirectory -Force

[xml]$project = Get-Content -LiteralPath (Join-Path $gameRoot 'SinStarI.smileproj') -Raw
$project.SmileProject.PropertyGroup.ApplicationId = 'smile.tests.sin-star-map-migration'
$project.SmileProject.PropertyGroup.RememberWindowPlacement = 'false'
foreach ($entry in @($project.SmileProject.ItemGroup.ChildNodes)) {
    if ($entry.Name -in @('Asset', 'Model3DAsset')) {
        $null = $entry.ParentNode.RemoveChild($entry)
    } elseif ($entry.HasAttribute('Include') -and $entry.Include -ne 'Program.smile') {
        $entry.SetAttribute('Include', [IO.Path]::GetRelativePath($testRoot,
            [IO.Path]::GetFullPath((Join-Path $gameRoot $entry.Include))))
    }
}
$project.Save((Join-Path $testRoot 'Maps.smileproj'))
$startup = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'MapAcceptanceTests.smile') -Raw).Replace('@EVIDENCE@', $EvidenceDirectory)
[IO.File]::WriteAllText((Join-Path $testRoot 'Program.smile'), $startup)
$exe = Join-Path $testRoot 'Maps.exe'
& (Join-Path $smileRoot 'artifacts\compiler\smilec.exe') --project (Join-Path $testRoot 'Maps.smileproj') --target windows-x64 --graphics DirectX -o $exe *> (Join-Path $testRoot 'compile.log')
if ($LASTEXITCODE -ne 0) {
    Get-Content -LiteralPath (Join-Path $testRoot 'compile.log') -Tail 25
    throw 'Map acceptance fixture did not compile.'
}
# Link published assets only after compilation, so the publisher cannot alter them.
$null = New-Item -ItemType Junction -Path (Join-Path $testRoot 'Assets') -Target (Join-Path $gameRoot 'bin\Release\Assets')
$process = Start-Process -FilePath $exe -WorkingDirectory $testRoot -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $testRoot 'run.log') -RedirectStandardError (Join-Path $testRoot 'error.log')
Write-Host "Map acceptance PID $($process.Id); logs: $testRoot"
$process.WaitForExit()
Get-Content -LiteralPath (Join-Path $testRoot 'run.log')
if ($process.ExitCode -ne 0 -or (Get-Content -LiteralPath (Join-Path $testRoot 'run.log') -Raw) -notmatch 'MAP_CHECK_FAILURES=0') {
    throw "Map acceptance failed. See $testRoot"
}
