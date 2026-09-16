param([int]$Port = 8765, [switch]$NoBrowser, [switch]$Stop, [string]$Page = '')
$ErrorActionPreference = 'Stop'
$siteRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
. (Join-Path $PSScriptRoot 'review-sequence/Save-ReviewSettings.ps1')
$address = "http://localhost:$Port/"
$pageAddress = $address + $Page.TrimStart('/')
function Open-SitePage {
    $chrome = Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe'
    if (Test-Path -LiteralPath $chrome) { Start-Process -FilePath $chrome -ArgumentList $pageAddress }
    else { Start-Process $pageAddress }
}
if ($Stop) {
    Invoke-WebRequest -Uri ($address + '__sinstar/stop') -Method Post | Out-Null
    exit
}
$existing = $null
try {
    $existing = Invoke-WebRequest -Uri ($address + '__sinstar/status') -TimeoutSec 2
} catch { }
if ($existing) {
    if ($existing.Content -ne $siteRoot) { throw "Port $Port is used by another website. Choose another port." }
    if (-not $NoBrowser) { Open-SitePage }
    exit
}

$listener = [Net.HttpListener]::new()
$listener.Prefixes.Add($address)
$listener.Start()
if (-not $NoBrowser) { Open-SitePage }
Write-Output "Sin Star I: $address"
$mime = @{'.html'='text/html; charset=utf-8'; '.css'='text/css'; '.js'='text/javascript';
    '.json'='application/json'; '.png'='image/png'; '.jpg'='image/jpeg'; '.jpeg'='image/jpeg';
    '.mp4'='video/mp4'; '.mp3'='audio/mpeg'; '.csv'='text/csv; charset=utf-8';
    '.svg'='image/svg+xml'; '.md'='text/plain; charset=utf-8'; '.ico'='image/x-icon'}
try {
    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $response = $context.Response
        $stream = $null
        try {
            $request = $context.Request
            $urlPath = [Uri]::UnescapeDataString($request.Url.AbsolutePath)
            $response.Headers['Cache-Control'] = 'no-cache'
            $response.Headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            if ($urlPath -eq '/__sinstar/status') {
                $bytes = [Text.Encoding]::UTF8.GetBytes($siteRoot)
                $response.ContentType = 'text/plain; charset=utf-8'
                $response.ContentLength64 = $bytes.Length
                $response.OutputStream.Write($bytes, 0, $bytes.Length)
                continue
            }
            if ($urlPath -eq '/__sinstar/stop' -and $request.HttpMethod -eq 'POST') {
                $bytes = [Text.Encoding]::UTF8.GetBytes('Stopped')
                $response.ContentType = 'text/plain; charset=utf-8'
                $response.ContentLength64 = $bytes.Length
                $response.OutputStream.Write($bytes, 0, $bytes.Length)
                break
            }
            if ($urlPath -eq '/__sinstar/review-settings' -and $request.HttpMethod -eq 'POST') {
                try {
                    Save-ReviewSettings $request $siteRoot
                    $result = @{ saved = $true } | ConvertTo-Json -Compress
                } catch {
                    $response.StatusCode = 400
                    $result = @{ error = $_.Exception.Message } | ConvertTo-Json -Compress
                }
                $bytes = [Text.Encoding]::UTF8.GetBytes($result)
                $response.ContentType = 'application/json'
                $response.ContentLength64 = $bytes.Length
                $response.OutputStream.Write($bytes, 0, $bytes.Length)
                continue
            }
            if ($request.HttpMethod -notin @('GET','HEAD')) { $response.StatusCode = 405; continue }
            if ($urlPath -eq '/') { $urlPath = '/index.html' }
            $path = [IO.Path]::GetFullPath((Join-Path $siteRoot $urlPath.TrimStart('/')))
            if (-not $path.StartsWith($siteRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or
                $urlPath -match '(^|[/\\])(\.[^/\\]*|local-state)([/\\]|$)' -or -not [IO.File]::Exists($path)) {
                $response.StatusCode = 404
                continue
            }
            $stream = [IO.File]::OpenRead($path)
            $length = $stream.Length
            $begin = 0L
            $end = $length - 1
            $response.ContentType = $mime[[IO.Path]::GetExtension($path).ToLowerInvariant()]
            if (-not $response.ContentType) { $response.ContentType = 'application/octet-stream' }
            $response.Headers['Accept-Ranges'] = 'bytes'
            $range = $request.Headers['Range']
            if ($range) {
                if ($range -notmatch '^bytes=(\d*)-(\d*)$' -or ($Matches[1] -eq '' -and $Matches[2] -eq '')) {
                    $response.StatusCode = 416; continue
                }
                if ($Matches[1] -eq '') { $begin = [Math]::Max(0L, $length - [long]$Matches[2]) }
                else {
                    $begin = [long]$Matches[1]
                    if ($Matches[2] -ne '') { $end = [Math]::Min($end, [long]$Matches[2]) }
                }
                if ($begin -gt $end -or $begin -ge $length) {
                    $response.StatusCode = 416
                    $response.Headers['Content-Range'] = "bytes */$length"
                    continue
                }
                $response.StatusCode = 206
                $response.Headers['Content-Range'] = "bytes $begin-$end/$length"
            }
            $response.ContentLength64 = $end - $begin + 1
            if ($request.HttpMethod -eq 'HEAD') { continue }
            $stream.Position = $begin
            $buffer = [byte[]]::new(65536)
            $remaining = $response.ContentLength64
            while ($remaining -gt 0) {
                $read = $stream.Read($buffer, 0, [int][Math]::Min($buffer.Length, $remaining))
                if ($read -eq 0) { break }
                $response.OutputStream.Write($buffer, 0, $read)
                $remaining -= $read
            }
        } catch {
            # Leaving a hover preview cancels its request; keep the local site available.
            Write-Verbose $_.Exception.Message
        } finally {
            if ($stream) { $stream.Dispose() }
            $response.Close()
        }
    }
} finally { $listener.Close() }
