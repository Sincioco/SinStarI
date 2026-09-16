param([switch]$ValidateOnly)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()
$siteRoot = Split-Path (Split-Path $PSScriptRoot)
$stateFolder = Join-Path $siteRoot 'production/local-state/review-sequence'
$progressPath = Join-Path $stateFolder 'progress.json'
$lockPath = Join-Path $stateFolder 'render.lock'
New-Item -ItemType Directory -Force -Path $stateFolder | Out-Null
$script:worker = $null
$script:outputFile = Join-Path $siteRoot 'asset/videos/Sin-Star-I-Story-Video-Sequence-Review.mp4'

$form = [System.Windows.Forms.Form]::new()
$form.Text = 'Sin Star I — Review Movie Builder'
$form.ClientSize = [System.Drawing.Size]::new(800, 410)
$form.StartPosition = 'CenterScreen'
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox = $false
$form.BackColor = [System.Drawing.Color]::FromArgb(12, 20, 34)
$form.ForeColor = [System.Drawing.Color]::FromArgb(240, 244, 250)
$form.Font = [System.Drawing.Font]::new('Segoe UI', 10)

function Add-Label($Text, $X, $Y, $Width, $Height) {
    $label = [System.Windows.Forms.Label]::new()
    $label.Text = $Text
    $label.SetBounds($X, $Y, $Width, $Height)
    $form.Controls.Add($label)
    return $label
}

function Add-Button($Text, $X, $Y, $Width) {
    $button = [System.Windows.Forms.Button]::new()
    $button.Text = $Text
    $button.SetBounds($X, $Y, $Width, 38)
    $button.FlatStyle = 'Flat'
    $button.BackColor = [System.Drawing.Color]::FromArgb(30, 47, 68)
    $form.Controls.Add($button)
    return $button
}

$logo = [System.Windows.Forms.PictureBox]::new()
$logo.SetBounds(24, 20, 95, 68)
$logo.SizeMode = 'Zoom'
$logo.Image = [System.Drawing.Image]::FromFile((Join-Path $siteRoot 'asset/images/smile-2.0-logo.png'))
$form.Controls.Add($logo)
$heading = Add-Label 'Sin Star I · Review Movie Builder' 139 24 635 36
$heading.Font = [System.Drawing.Font]::new('Segoe UI', 18, [System.Drawing.FontStyle]::Bold)
$null = Add-Label 'Edit the sequence and volume settings, then render your review.' 140 65 630 28
$null = Add-Label 'Configuration' 24 114 735 25
$configBox = [System.Windows.Forms.TextBox]::new()
$configBox.SetBounds(24, 143, 614, 28)
$configBox.Text = Join-Path $PSScriptRoot 'sequence.json'
$form.Controls.Add($configBox)
$browse = Add-Button 'Browse…' 652 138 122
$edit = Add-Button 'Edit JSON' 24 189 100
$preview = Add-Button 'Play Sequence' 134 189 138
$render = Add-Button 'Render Movie' 282 189 133
$cancel = Add-Button 'Cancel Render' 425 189 119
$open = Add-Button 'Play Movie' 554 189 106
$folder = Add-Button 'Open Folder' 670 189 104
$gauge = [System.Windows.Forms.ProgressBar]::new()
$gauge.SetBounds(24, 252, 750, 22)
$form.Controls.Add($gauge)
$status = Add-Label 'Ready. No files are uploaded by this program.' 24 284 750 53
$note = Add-Label 'Rendering runs in the background. Closing this window keeps the render running.' 24 348 750 48
$note.ForeColor = [System.Drawing.Color]::FromArgb(177, 193, 212)

$browse.Add_Click({
    $dialog = [System.Windows.Forms.OpenFileDialog]::new()
    $dialog.Filter = 'JSON sequence (*.json)|*.json'
    $dialog.InitialDirectory = $PSScriptRoot
    if ($dialog.ShowDialog() -eq 'OK') { $configBox.Text = $dialog.FileName }
    $dialog.Dispose()
})
$edit.Add_Click({
    $start = [System.Diagnostics.ProcessStartInfo]::new('notepad.exe')
    $start.ArgumentList.Add($configBox.Text)
    $null = [System.Diagnostics.Process]::Start($start)
})
$preview.Add_Click({
    try {
        $configPath = [IO.Path]::GetFullPath($configBox.Text)
        if (-not $configPath.StartsWith($siteRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
            throw 'Keep the JSON configuration inside the website folder for live playback.'
        }
        $relative = [IO.Path]::GetRelativePath($siteRoot, $configPath).Replace('\', '/')
        $page = 'review.html?config=' + [Uri]::EscapeDataString($relative)
        $start = [System.Diagnostics.ProcessStartInfo]::new((Get-Command pwsh).Source)
        $start.UseShellExecute = $false
        $start.CreateNoWindow = $true
        foreach ($argument in @('-NoProfile', '-File', (Join-Path $siteRoot 'production/serve.ps1'), '-Page', $page)) {
            $start.ArgumentList.Add($argument)
        }
        $null = [System.Diagnostics.Process]::Start($start)
    } catch {
        [System.Windows.Forms.MessageBox]::Show($_.Exception.Message, 'Could Not Open Sequence')
    }
})
$render.Add_Click({
    try {
        if (Test-Path -LiteralPath $lockPath) { throw 'Another render is already running.' }
        $settings = Get-Content -LiteralPath $configBox.Text -Raw | ConvertFrom-Json
        $script:outputFile = Join-Path $siteRoot $settings.output
        $bundled = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
        $python = if (Test-Path -LiteralPath $bundled) { $bundled } else { (Get-Command python -ErrorAction Stop).Source }
        $start = [System.Diagnostics.ProcessStartInfo]::new($python)
        $start.WorkingDirectory = $siteRoot
        $start.UseShellExecute = $false
        $start.CreateNoWindow = $true
        foreach ($argument in @('-X', 'utf8', (Join-Path $PSScriptRoot 'render_review.py'), '--config', $configBox.Text)) {
            $start.ArgumentList.Add($argument)
        }
        $script:worker = [System.Diagnostics.Process]::Start($start)
        $status.Text = 'Starting the renderer…'
        $render.Enabled = $false
    } catch {
        [System.Windows.Forms.MessageBox]::Show($_.Exception.Message, 'Could Not Start Render')
    }
})
$cancel.Add_Click({
    Set-Content -LiteralPath (Join-Path $stateFolder 'cancel.request') -Value 'Cancel' -Encoding utf8
    $status.Text = 'Cancelling after the current FFmpeg progress update…'
})
$open.Add_Click({
    if (Test-Path -LiteralPath $script:outputFile) {
        $start = [System.Diagnostics.ProcessStartInfo]::new($script:outputFile)
        $start.UseShellExecute = $true
        $null = [System.Diagnostics.Process]::Start($start)
    }
})
$folder.Add_Click({
    $start = [System.Diagnostics.ProcessStartInfo]::new('explorer.exe')
    $start.ArgumentList.Add((Split-Path $script:outputFile))
    $null = [System.Diagnostics.Process]::Start($start)
})
$timer = [System.Windows.Forms.Timer]::new()
$timer.Interval = 500
$timer.Add_Tick({
    $busy = Test-Path -LiteralPath $lockPath
    if ($script:worker -and -not $script:worker.HasExited) { $busy = $true }
    $render.Enabled = -not $busy
    $browse.Enabled = -not $busy
    $configBox.Enabled = -not $busy
    $cancel.Enabled = $busy
    $open.Enabled = Test-Path -LiteralPath $script:outputFile
    if (Test-Path -LiteralPath $progressPath) {
        try {
            $share = [IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete
            $stream = [IO.File]::Open($progressPath, [IO.FileMode]::Open, [IO.FileAccess]::Read, $share)
            $reader = [IO.StreamReader]::new($stream)
            try { $progress = $reader.ReadToEnd() | ConvertFrom-Json }
            finally { $reader.Dispose() }
            $gauge.Value = [Math]::Clamp([int]$progress.percent, 0, 100)
            $status.Text = "$($progress.percent)% · $($progress.phase)"
            if ($progress.output) { $script:outputFile = $progress.output }
        } catch { }
    }
    if ($script:worker -and $script:worker.HasExited -and $script:worker.ExitCode -ne 0) {
        if (-not $progress -or $progress.pid -ne $script:worker.Id) {
            $status.Text = 'Renderer could not start. Check that Python/Pillow and FFmpeg are installed.'
        }
        $script:worker.Dispose()
        $script:worker = $null
    }
})
$form.Add_FormClosed({ $timer.Stop() })
if ($ValidateOnly) {
    Write-Output "UI constructed: $($form.Controls.Count) controls; configuration $($configBox.Text)"
} else {
    $timer.Start()
    [System.Windows.Forms.Application]::Run($form)
}
$timer.Dispose()
$logo.Image.Dispose()
$form.Dispose()
