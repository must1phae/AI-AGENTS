param(
    [string]$TaskName = "AI-AGENTS-DailyPost",
    [string]$StartTime = "09:00"
)

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$mainScript = Join-Path $projectRoot "main.py"

if (-not (Test-Path $pythonExe)) {
    throw "Python executable not found: $pythonExe"
}
if (-not (Test-Path $mainScript)) {
    throw "Main script not found: $mainScript"
}

$timeParts = $StartTime.Split(":")
if ($timeParts.Count -ne 2) {
    throw "StartTime must be in HH:mm format."
}

$hour = [int]$timeParts[0]
$minute = [int]$timeParts[1]
$startAt = (Get-Date).Date.AddHours($hour).AddMinutes($minute)

$action = New-ScheduledTaskAction -Execute $pythonExe -Argument ('"{0}"' -f $mainScript)
$trigger = New-ScheduledTaskTrigger -Daily -At $startAt

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Description "Daily AI AGENTS post" -Force | Out-Null

Write-Output "Task '$TaskName' created/updated."
Write-Output "Schedule: every day at $StartTime"
Write-Output "Execute: $pythonExe"
Write-Output "Arguments: \"$mainScript\""
