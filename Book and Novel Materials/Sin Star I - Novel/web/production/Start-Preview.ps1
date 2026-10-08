[CmdletBinding()]
param([string]$Root='D:\My Documents - 2026\SinStar_Audio_BookOne\docs',[int]$Port=8897)
$ErrorActionPreference='Stop'
$resolvedRoot=(Resolve-Path -LiteralPath $Root).Path
$healthUrl="http://127.0.0.1:$Port/__preview_health"
try { $existing=Invoke-RestMethod -Uri $healthUrl -TimeoutSec 2 } catch { $existing=$null }
if($existing){
    if($existing.service -ne 'Sin Star Book One preview' -or $existing.root -ne $resolvedRoot){throw 'Port is serving a different preview. Leave it intact and choose another port.'}
    $existing | ConvertTo-Json
    return
}
$pythonw=(Get-Command pythonw.exe -ErrorAction Stop).Source
$script=Join-Path $PSScriptRoot 'preview_server.py'
$command='"'+$pythonw+'" "'+$script+'" --root "'+$resolvedRoot+'" --port '+$Port
# WMI owns the child, so ending the Codex command/task does not terminate it.
# pythonw keeps the server window hidden. No scheduled task or startup entry is made.
$created=Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine=$command;CurrentDirectory=$PSScriptRoot}
if($created.ReturnValue -ne 0){throw "Preview launch failed: $($created.ReturnValue)"}
for($attempt=0;$attempt -lt 20;$attempt++){
    try {$health=Invoke-RestMethod -Uri $healthUrl -TimeoutSec 2;break} catch {Start-Sleep -Milliseconds 150}
}
if(!$health -or $health.pid -ne $created.ProcessId -or $health.root -ne $resolvedRoot){throw 'Preview did not become ready. Inspect the local preview log.'}
$health | ConvertTo-Json
