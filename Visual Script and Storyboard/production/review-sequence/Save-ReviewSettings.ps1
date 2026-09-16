# Only review preferences may be written through the local player. Story text and paths stay intact.
function Save-ReviewSettings($Request, [string]$SiteRoot) {
    if (-not $Request.IsLocal -or $Request.Headers['Origin'] -ne $Request.Url.GetLeftPart([UriPartial]::Authority) -or
        $Request.ContentType -notlike 'application/json*' -or $Request.ContentLength64 -lt 1 -or $Request.ContentLength64 -gt 1048576) {
        throw 'Expected a local, same-origin JSON request.'
    }
    $reader = [IO.StreamReader]::new($Request.InputStream, [Text.Encoding]::UTF8)
    try { $patch = $reader.ReadToEnd() | ConvertFrom-Json -AsHashtable -Depth 30 }
    finally { $reader.Dispose() }
    $reviewRoot = Join-Path $SiteRoot 'production/review-sequence'
    $path = [IO.Path]::GetFullPath((Join-Path $SiteRoot ([string]$patch.config)))
    if (-not $path.StartsWith($reviewRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or
        [IO.Path]::GetExtension($path) -ne '.json' -or -not [IO.File]::Exists($path)) { throw 'Choose a review sequence JSON in production/review-sequence.' }
    $original = [IO.File]::ReadAllText($path)
    $config = $original | ConvertFrom-Json -AsHashtable -Depth 40
    if (-not $config.clips -or -not $config.audio -or -not $config.opening -or -not $config.credits) { throw 'This file is not a review sequence.' }
    if ([int]$patch.panel_layout_version -ne [int]$config.panel_layout_version -and $patch.clips -and
        @($patch.clips.Values | Where-Object { $_.ContainsKey('panel_positions') }).Count) {
        throw 'Panel positions were reset. Reload Video Clips before saving new positions.'
    }
    $corners = @('upper-left', 'upper-right', 'lower-left', 'lower-right')
    foreach ($key in @('clip_volume', 'music_volume', 'master_volume')) {
        if ($patch.audio -and $patch.audio.ContainsKey($key)) {
            $value = $patch.audio[$key]
            if ($value -is [string] -or $value -is [bool] -or $null -eq $value -or
                -not [double]::IsFinite([double]$value) -or $value -lt 0 -or $value -gt 2) { throw 'Volume must be from 0 to 2.' }
            $config.audio[$key] = $value
        }
    }
    if ($patch.settings) {
        if ($patch.settings.ContainsKey('layout')) {
            if ($patch.settings.layout -notin @('overlay', 'side-by-side')) { throw 'Unknown layout.' }
            $config.settings.layout = $patch.settings.layout
        }
        if ($patch.settings.ContainsKey('show_labels')) {
            if ($patch.settings.show_labels -isnot [bool]) { throw 'Show Labels must be true or false.' }
            $config.settings.show_labels = $patch.settings.show_labels
        }
    }
    if ($patch.clips) {
        foreach ($id in $patch.clips.Keys) {
            $clip = $config.clips | Where-Object { $_.id -ceq $id } | Select-Object -First 1
            if (-not $clip) { throw "Unknown clip ID: $id" }
            $change = $patch.clips[$id]
            if ($change.ContainsKey('muted')) {
                if ($change.muted -isnot [bool]) { throw 'Muted must be true or false.' }
                $clip.muted = $change.muted
            }
            if ($change.ContainsKey('panel_positions')) {
                $positions = $change.panel_positions
                if ($positions.scene_info -notin $corners -or $positions.scene_context -notin $corners -or
                    $positions.scene_info -eq $positions.scene_context) { throw 'Choose two different panel corners.' }
                $clip.panel_positions = @{ scene_info = $positions.scene_info; scene_context = $positions.scene_context }
            }
        }
    }
    $temporary = $path + '.' + [Guid]::NewGuid().ToString('N') + '.tmp'
    try {
        [IO.File]::WriteAllText($temporary, ($config | ConvertTo-Json -Depth 40) + "`n", [Text.UTF8Encoding]::new($false))
        if ([IO.File]::ReadAllText($path) -cne $original) { throw 'The JSON changed during saving. Retry the change.' }
        [IO.File]::Move($temporary, $path, $true)
    } finally { if ([IO.File]::Exists($temporary)) { [IO.File]::Delete($temporary) } }
}
