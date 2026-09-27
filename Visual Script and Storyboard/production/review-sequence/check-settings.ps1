# Focused HTTP regression: resetting positions must not reject unrelated audio saves.
param([int]$Port = 8765)
$ErrorActionPreference = 'Stop'
$siteRoot = Split-Path (Split-Path $PSScriptRoot)
$address = "http://localhost:$Port"
if ((Invoke-WebRequest "$address/__sinstar/status").Content -ne $siteRoot) { throw 'Unexpected local server.' }
$relative = 'production/review-sequence/settings-check-' + [Guid]::NewGuid().ToString('N') + '.json'
$testPath = Join-Path $siteRoot $relative
$config = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'sequence.json') -Raw | ConvertFrom-Json -AsHashtable
$config.panel_layout_version = 1
$id = $config.clips[0].id
$config.clips[0].Remove('panel_positions')
function Send-Settings($Patch) {
    $Patch.config = $relative
    return Invoke-WebRequest "$address/__sinstar/review-settings" -Method Post -Headers @{ Origin = $address } `
        -ContentType 'application/json' -Body ($Patch | ConvertTo-Json -Depth 10) -SkipHttpErrorCheck
}
try {
    [IO.File]::WriteAllText($testPath, ($config | ConvertTo-Json -Depth 40))
    $patch = @{ clips = @{ $id = @{ panel_positions = @{ scene_info = 'upper-left'; scene_context = 'upper-right' } } } }
    if ((Send-Settings $patch).StatusCode -ne 400) { throw 'A stale tab restored panel positions.' }
    $saved = Get-Content -LiteralPath $testPath -Raw | ConvertFrom-Json
    if ($saved.clips[0].panel_positions) { throw 'Rejected positions reached disk.' }
    $patch.panel_layout_version = 1
    if ((Send-Settings $patch).StatusCode -ne 200) { throw 'Current panel save failed.' }
    $saved = Get-Content -LiteralPath $testPath -Raw | ConvertFrom-Json
    if ($saved.clips[0].panel_positions.scene_context -ne 'upper-right') { throw 'New panel position did not save.' }
    # Missing clips previously caused a null-method error when the layout version differed.
    if ((Send-Settings @{ audio = @{ music_volume = 0.23 } }).StatusCode -ne 200) { throw 'Audio-only save failed after reset.' }
    if ((Send-Settings @{ clips = @{ $id = @{ muted = $true } } }).StatusCode -ne 200) { throw 'Mute-only save failed after reset.' }
    $saved = Get-Content -LiteralPath $testPath -Raw | ConvertFrom-Json
    if ($saved.audio.music_volume -ne 0.23 -or -not $saved.clips[0].muted) { throw 'Audio changes did not reach disk.' }
    $before = $saved.clips[0].file
    if ((Send-Settings @{ clips = @{ $id = @{ enabled = $false } } }).StatusCode -ne 200) { throw 'Exclusion save failed.' }
    $saved = Get-Content -LiteralPath $testPath -Raw | ConvertFrom-Json
    if ($saved.clips[0].enabled -ne $false -or $saved.clips[0].file -ne $before -or -not $saved.clips[0].muted) { throw 'Exclusion lost or changed unrelated settings.' }
    if ((Send-Settings @{ clips = @{ $id = @{ enabled = 'false' } } }).StatusCode -ne 400) { throw 'Invalid exclusion accepted.' }
    if ((Send-Settings @{ clips = @{ $id = @{ enabled = $true } } }).StatusCode -ne 200) { throw 'Re-inclusion failed.' }
    $saved = Get-Content -LiteralPath $testPath -Raw | ConvertFrom-Json
    if ($saved.clips[0].enabled -ne $true) { throw 'Re-inclusion did not reach disk.' }
    Write-Output 'Passed: stale positions rejected; layout/audio/mute preserved; exclusion and re-inclusion persisted; invalid inclusion rejected.'
} finally {
    if ([IO.File]::Exists($testPath)) { [IO.File]::Delete($testPath) }
}
