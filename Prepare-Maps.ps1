[CmdletBinding()]
param([string]$SmileRoot = (Join-Path $PSScriptRoot '..\SMILE 2.0'))

$ErrorActionPreference = 'Stop'
$library = Get-Content -LiteralPath (Join-Path $SmileRoot 'tools\Character3DViewer\TownLibrary.smile') -Raw
$nameSection = $library.Substring(0, $library.IndexOf('Public Function PermanentKey'))
$names = @([regex]::Matches($nameSection, 'Return "([^"]+)"') | ForEach-Object { $_.Groups[1].Value })
$destination = Join-Path $PSScriptRoot 'Assets\Maps'
$null = New-Item -ItemType Directory -Path $destination -Force
foreach ($name in $names) {
    $source = if ($name -eq 'Neris Metropolis') {
        Join-Path $PSScriptRoot "SourceAssets\Towns\Neris\NerisMetropolisV1\Town\$name.town"
    } else {
        Join-Path $PSScriptRoot "SourceAssets\Towns\Neris\StoryTownsV1\Towns\$name.town"
    }
    $preview = Join-Path $PSScriptRoot "Maps\Previews\$name.png"
    if (-not (Test-Path -LiteralPath $source)) { throw "Missing authored map: $source" }
    if (-not (Test-Path -LiteralPath $preview)) { throw "Missing map thumbnail: $preview" }
    # The native asset reader accepts executable-relative paths. Prepare the
    # existing bundle records once here, keeping file-picker paths out of play.
    $bundle = [IO.File]::ReadAllBytes($source)
    $records = [Collections.Generic.List[object]]::new()
    $mainLength = 44 + [BitConverter]::ToUInt32($bundle, 8)
    $records.Add(@{ Suffix = '-'; Offset = 0; Length = $mainLength })
    $offset = $mainLength
    if ($offset -lt $bundle.Length) {
        if ([Text.Encoding]::ASCII.GetString($bundle, $offset, 4) -ne 'SMB1') { throw "Invalid town bundle: $name" }
        $digest = [Security.Cryptography.SHA256]::HashData($bundle[0..($bundle.Length - 33)])
        if ([Convert]::ToHexString($digest) -ne [Convert]::ToHexString($bundle[($bundle.Length - 32)..($bundle.Length - 1)])) { throw "Town bundle checksum failed: $name" }
        $count = [BitConverter]::ToUInt32($bundle, $offset + 4)
        $offset += 8
        for ($index = 0; $index -lt $count; $index++) {
            $nameLength = [BitConverter]::ToUInt32($bundle, $offset)
            $length = [BitConverter]::ToUInt32($bundle, $offset + 4)
            $offset += 8
            $suffix = [Text.Encoding]::UTF8.GetString($bundle, $offset, $nameLength)
            $offset += $nameLength
            $records.Add(@{ Suffix = $suffix; Offset = $offset; Length = $length })
            $offset += $length
        }
    }
    $recordRoot = Join-Path $destination $name
    $null = New-Item -ItemType Directory -Path $recordRoot -Force
    $index = 0
    foreach ($record in $records) {
        $start = $record.Offset
        $size = [BitConverter]::ToUInt32($bundle, $start + 8)
        if ([Text.Encoding]::ASCII.GetString($bundle, $start, 4) -ne 'SMD4' -or $record.Length -ne $size + 44 -or $size -gt 1048576) { throw "Invalid map record: $name $($record.Suffix)" }
        $payload = $bundle[($start + 44)..($start + 43 + $size)]
        $digest = [Security.Cryptography.SHA256]::HashData([byte[]]$payload)
        if ([Convert]::ToHexString($digest) -ne [Convert]::ToHexString($bundle[($start + 12)..($start + 43)])) { throw "Map record checksum failed: $name $($record.Suffix)" }
        # A fixed prefix prevents the text-file byte reader from interpreting a
        # coincidental UTF-8 BOM at the beginning of a binary payload.
        [IO.File]::WriteAllBytes((Join-Path $recordRoot "$index.mapdata"), [byte[]](@(0) + $payload))
        $index++
    }
    [IO.File]::WriteAllText((Join-Path $recordRoot 'records.txt'), (($records.Suffix -join "`n") + "`n"))
    Copy-Item -LiteralPath $preview -Destination (Join-Path $destination "$name.png") -Force
}
Write-Host "Prepared $($names.Count) maps and matching thumbnail assets."
