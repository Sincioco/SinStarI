[CmdletBinding()]
param([int]$Port=8897)
$ErrorActionPreference='Stop'
$health=Invoke-RestMethod -Uri "http://127.0.0.1:$Port/__preview_health" -TimeoutSec 2
if($health.service -ne 'Sin Star Book One preview'){throw 'This is not the reader preview.'}
$serverProcess=Get-CimInstance Win32_Process -Filter "ProcessId=$($health.pid)"
if(!$serverProcess -or $serverProcess.Name -ne 'pythonw.exe' -or $serverProcess.CommandLine -notlike '*preview_server.py*'){throw 'Preview process identity does not match; left running.'}
Stop-Process -Id $serverProcess.ProcessId
Write-Output "Reader preview stopped on port $Port. Browser data was not changed."
