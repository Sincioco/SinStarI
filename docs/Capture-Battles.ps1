[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$gameRoot = Split-Path $PSScriptRoot -Parent
$smileRoot = [IO.Path]::GetFullPath((Join-Path $gameRoot '..\SMILE 2.0'))
$testRoot = Join-Path $gameRoot ('artifacts\battle-photos-' + [Guid]::NewGuid().ToString('N'))
$evidence = Join-Path $PSScriptRoot 'images\battles'
$null = New-Item -ItemType Directory -Path $testRoot, $evidence -Force
[xml]$project = Get-Content -LiteralPath (Join-Path $gameRoot 'SinStarI.smileproj') -Raw
$project.SmileProject.PropertyGroup.ApplicationId = 'smile.tests.sin-star-battle-photos'
$project.SmileProject.PropertyGroup.RememberWindowPlacement = 'false'
$project.SmileProject.PropertyGroup.VSync = 'false'
foreach ($entry in @($project.SmileProject.ItemGroup.ChildNodes)) {
    if ($entry.Name -in @('Asset', 'Model3DAsset')) {
        $null = $entry.ParentNode.RemoveChild($entry)
    } elseif ($entry.HasAttribute('Include') -and $entry.Include -ne 'Program.smile') {
        $entry.SetAttribute('Include', [IO.Path]::GetRelativePath($testRoot,
            [IO.Path]::GetFullPath((Join-Path $gameRoot $entry.Include))))
    }
}
# Observe the real choreography in a disposable copy. Production sources and
# gameplay are unchanged; a fixed frame step makes the photograph run repeatable.
$workflow = Get-Content -LiteralPath (Join-Path $smileRoot 'tools\Character3DViewer\ViewerWorkflow.smile') -Raw
$probe = @'
    Public Sub PhotographStep()
        Me.Timing.PreviousTime = Timer() - 32
        Call Me.UpdateFrame(640, 384)
    End Sub

    Public Function PhotographActor() As Number
        Dim Duration As Number
        Dim Elapsed As Number
        If Me.Party.AttackCycle <> 2 Or Me.Party.Stage <> 1 Then
            Return -1
        End If
        Duration = ViewerParty.AttackDuration(Me.Party, Me.Character,
            Me.Party.Companion.Actor, Me.Playback.PlaybackSpeed)
        Elapsed = Me.Party.Elapsed - ViewerParty.HERO_ATTACK_START_MILLISECONDS
        If Not Me.Party.UnityRoster Then
            Elapsed = Me.Party.Elapsed - 1300
        End If
        If Elapsed < Duration * 45 / 100 Or Elapsed > Duration * 70 / 100 Then
            Return -1
        End If
        If Me.Party.Turn = 0 Then
            Return 0
        Else If Me.Party.Turn = 1 Then
            Return 1
        Else If Me.Party.Turn = 5 Then
            Return 2
        Else If Me.Party.Turn = 6 Then
            Return 3
        End If
        Return -1
    End Function

    Public Sub FrameHealingPhotograph()
        Me.ViewerCameraState.Live = ViewerParty.FormationCamera(Me.ViewerCameraState.Base, 0)
    End Sub


'@
$workflow = $workflow.Replace('    Public Function PresentationCaption() As Text', $probe + '    Public Function PresentationCaption() As Text')
[IO.File]::WriteAllText((Join-Path $testRoot 'ViewerWorkflow.smile'), $workflow)
($project.SmileProject.ItemGroup.SmileSource | Where-Object {$_.Include.EndsWith('ViewerWorkflow.smile')}).SetAttribute('Include', 'ViewerWorkflow.smile')
$project.Save((Join-Path $testRoot 'Photos.smileproj'))
$startup = @'
Option Explicit
Import Smile.Tools.Character3DViewerWorkflow As Viewer
Import Smile.Simple3D.Graphics3D As G
Dim Preview As Viewer.Session
Dim Seen[4] As Boolean
Dim Heroes[4] As Text
Dim Bosses[3] As Text
Dim Tabs[3] As Number
Dim Boss As Number
Dim Actor As Number
Dim Index As Number
Dim Total As Number
Dim Frame As Number
Dim Capture As Number
Dim Job As Number
Dim Deadline As Number
Dim ViewportReady As Boolean
Game Window "Sin Star I Battle Photographs" Size 640 By 384
Clear BLACK
Show Screen
Heroes[0] = "Arin"
Heroes[1] = "Orin"
Heroes[2] = "Zara"
Heroes[3] = "Mira"
Bosses[0] = "Vrax"
Bosses[1] = "Kael"
Bosses[2] = "Dragon"
Tabs[0] = 3
Tabs[1] = 14
Tabs[2] = 7
For Boss = 0 To 2
    Print "Opening " + Bosses[Boss] + " battle"
    Preview = New Viewer.Session()
    Call Preview.Start(Tabs[Boss], True, 640, 384)
    Total = 0
    For Index = 0 To 3
        Seen[Index] = False
    End For
    For Frame = 0 To 12000
        Call Preview.PhotographStep()
        If Not Preview.SceneReady() Then
            Print "FAIL scene " + Bosses[Boss]
            Exit For
        End If
        Actor = Preview.PhotographActor()
        If Frame Mod 16 = 0 Or Actor >= 0 Then
            ViewportReady = G.SetViewport3D(0, 0, 640, 384, True)
            If Actor = 3 Then
                Call Preview.FrameHealingPhotograph()
            End If
            Call Preview.DrawFrame()
            Show Screen
        End If
        If Actor >= 0 Then
            If Not Seen[Actor] Then
                Capture = G.CaptureViewport3D()
                Job = G.ExportViewportCapturePng3D(Capture,
                    "@EVIDENCE@\" + Bosses[Boss] + "-" + Heroes[Actor] + ".png")
                Deadline = Timer() + 10000
                Do
                    Show Screen
                Loop Until Data_FileStatus(Job) <> 0 Or Timer() > Deadline
                If Capture > 0 And Job > 0 And Data_FileStatus(Job) = 1 Then
                    Print "PASS " + Bosses[Boss] + " / " + Preview.PresentationCaption()
                    Seen[Actor] = True
                    Total = Total + 1
                Else
                    Print "FAIL photograph " + Bosses[Boss] + " / " + Heroes[Actor]
                    Exit For
                End If
                Call G.ReleaseViewportCapture3D(Capture)
            End If
        End If
        If Total = 4 Or Game_Closed() Then
            Exit For
        End If
    End For
    Call Preview.Release()
    Preview = Nothing
End For
End Program
'@
$startup = $startup.Replace('@EVIDENCE@', $evidence)
[IO.File]::WriteAllText((Join-Path $testRoot 'Program.smile'), $startup)
$exe = Join-Path $testRoot 'Photos.exe'
& (Join-Path $smileRoot 'artifacts\compiler\smilec.exe') --project (Join-Path $testRoot 'Photos.smileproj') --target windows-x64 --graphics DirectX -o $exe *> (Join-Path $testRoot 'compile.log')
if ($LASTEXITCODE -ne 0) {
    Get-Content -LiteralPath (Join-Path $testRoot 'compile.log') -Tail 20
    throw 'Battle photograph fixture did not compile.'
}
$null = New-Item -ItemType Junction -Path (Join-Path $testRoot 'Assets') -Target (Join-Path $gameRoot 'bin\Release\Assets')
$null = New-Item -ItemType Junction -Path (Join-Path $testRoot 'TechnicalAssets') -Target (Join-Path $gameRoot 'bin\Release\TechnicalAssets')
$process = Start-Process -FilePath $exe -WorkingDirectory $testRoot -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $testRoot 'run.log') -RedirectStandardError (Join-Path $testRoot 'error.log')
Write-Host "Battle photographs PID $($process.Id); logs: $testRoot"
$process.WaitForExit()
$lines = Get-Content -LiteralPath (Join-Path $testRoot 'run.log')
$lines
if ($process.ExitCode -ne 0 -or @($lines | Where-Object {$_ -like 'PASS *'}).Count -ne 12) {
    throw "Battle photographs incomplete. See $testRoot"
}
