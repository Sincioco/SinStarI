[CmdletBinding()]
param(
    [ValidateSet('Debug', 'Release')]
    [string]$Configuration = 'Release',
    [switch]$PrepareOnly
)

$ErrorActionPreference = 'Stop'
$gameRoot = $PSScriptRoot
$repositoryRoot = [IO.Path]::GetFullPath((Join-Path $gameRoot '..\SMILE 2.0'))
$viewerRoot = Join-Path $repositoryRoot 'tools\Character3DViewer'
$compiler = Join-Path $repositoryRoot 'artifacts\compiler\smilec.exe'
$projectPath = Join-Path $gameRoot 'SinStarI.smileproj'

# Reuse the established canonical package, local Unity audio and calibration preparation.
# This prepares inputs only; it neither launches the editor nor runs a Web build.
& (Join-Path $viewerRoot 'Build.ps1') -Target Native -PrepareOnly `
    -OutputDirectory (Join-Path $gameRoot 'artifacts\studio-preparation')
[xml]$viewerProject = Get-Content -LiteralPath (Join-Path $viewerRoot 'Character3DViewer.smileproj') -Raw
[xml]$gameProject = Get-Content -LiteralPath $projectPath -Raw
$gameSources = @($gameProject.SmileProject.ItemGroup.SmileSource | ForEach-Object {
    [IO.Path]::GetFullPath((Join-Path $gameRoot $_.Include))
})
foreach ($source in $viewerProject.SmileProject.ItemGroup.SmileSource) {
    if ($source.StartupOnly -eq 'true') { continue }
    $sourcePath = [IO.Path]::GetFullPath((Join-Path $viewerRoot $source.Include))
    $oldGameRoot = Join-Path $repositoryRoot 'games\SinStarI'
    if ($sourcePath.StartsWith($oldGameRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        $sourcePath = Join-Path $gameRoot ([IO.Path]::GetRelativePath($oldGameRoot, $sourcePath))
    }
    if ($sourcePath -notin $gameSources) {
        throw "Sin Star I must link the current shared presentation source: $sourcePath"
    }
}

$inputs = @($viewerProject.SmileProject.ItemGroup.Asset | ForEach-Object {
    Get-ChildItem -Path (Join-Path $viewerRoot $_.Include) -File
})
foreach ($model in $gameProject.SmileProject.ItemGroup.Model3DAsset) {
    if (-not $model.Include.StartsWith('BuildAssets\')) { continue }
    $directory = Split-Path (Join-Path $viewerRoot $model.Include) -Parent
    $inputs += Get-ChildItem -LiteralPath $directory -File -Recurse
}
foreach ($inputFile in $inputs | Sort-Object FullName -Unique) {
    $relative = [IO.Path]::GetRelativePath($viewerRoot, $inputFile.FullName)
    $destination = Join-Path $gameRoot $relative
    $null = New-Item -ItemType Directory -Path (Split-Path $destination -Parent) -Force
    Copy-Item -LiteralPath $inputFile.FullName -Destination $destination -Force
}

& (Join-Path $gameRoot 'Prepare-Maps.ps1') -SmileRoot $repositoryRoot

if ($PrepareOnly) {
    Write-Host "Prepared native Sin Star I inputs: $projectPath"
    return
}

$outputDirectory = Join-Path $gameRoot "bin\$Configuration"
$null = New-Item -ItemType Directory -Path $outputDirectory -Force
$output = Join-Path $outputDirectory 'SinStarI.exe'
[string[]]$debugArguments = if ($Configuration -eq 'Debug') { @('--debug') } else { @() }
& $compiler --project $projectPath --target windows-x64 --configuration $Configuration `
    --graphics DirectX -o $output @debugArguments
if ($LASTEXITCODE -ne 0) { throw 'Native Sin Star I compilation failed.' }
Write-Host "Built Sin Star I: $output"
