[CmdletBinding()]
param([switch]$Inspect)

$ErrorActionPreference = 'Stop'
$gameRoot = Split-Path $PSScriptRoot -Parent
$smileRoot = [IO.Path]::GetFullPath((Join-Path $gameRoot '..\SMILE 2.0'))
$testRoot = Join-Path $gameRoot ('artifacts\armory-check-' + [Guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $testRoot
[xml]$project = Get-Content -LiteralPath (Join-Path $gameRoot 'SinStarI.smileproj') -Raw
$project.SmileProject.PropertyGroup.ApplicationId = 'smile.tests.garran-armory'
$project.SmileProject.PropertyGroup.RememberWindowPlacement = 'false'
foreach ($entry in @($project.SmileProject.ItemGroup.ChildNodes)) {
    if ($entry.Name -in @('Asset', 'Model3DAsset')) {
        $null = $entry.ParentNode.RemoveChild($entry)
    } elseif ($entry.HasAttribute('Include') -and $entry.Include -ne 'Program.smile') {
        $entry.SetAttribute('Include', [IO.Path]::GetFullPath((Join-Path $gameRoot $entry.Include)))
    }
}
$project.Save((Join-Path $testRoot 'Armory.smileproj'))
$startup = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'ArmoryAcceptanceTests.smile') -Raw
$startup = $startup.Replace('@INSPECT@', $(if ($Inspect) { 'True' } else { 'False' }))
[IO.File]::WriteAllText((Join-Path $testRoot 'Program.smile'), $startup)
$exe = Join-Path $testRoot 'Armory.exe'
& (Join-Path $smileRoot 'artifacts\compiler\smilec.exe') --project (Join-Path $testRoot 'Armory.smileproj') --target windows-x64 --graphics DirectX -o $exe *> (Join-Path $testRoot 'compile.log')
if ($LASTEXITCODE -ne 0) {
    Get-Content -LiteralPath (Join-Path $testRoot 'compile.log') -Tail 25
    throw 'Armory fixture did not compile.'
}
# This isolated output cannot publish over the user's live assets or save identity.
$null = New-Item -ItemType Junction -Path (Join-Path $testRoot 'Assets') -Target (Join-Path $gameRoot 'bin\Release\Assets')
Write-Host "Armory evidence: $testRoot"
if ($Inspect) {
    Start-Process -FilePath $exe -WorkingDirectory $testRoot -PassThru -RedirectStandardOutput (Join-Path $testRoot 'run.log')
} else {
    & (Join-Path $smileRoot 'scripts\Invoke-TownNativeCheck.ps1') -Executable $exe `
        -Expected 'Garran armory native acceptance PASS' -LogPrefix (Join-Path $testRoot 'run') -TimeoutSeconds 180
}
