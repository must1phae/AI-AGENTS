param(
    [string]$TaskName = "AI-AGENTS-DailyPost",
    [string]$StartTime = "09:00",
    [switch]$PerAgentScheduler
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

if ($PerAgentScheduler) {
    $schedulerTaskName = if ([string]::IsNullOrWhiteSpace($TaskName) -or $TaskName -eq "AI-AGENTS-DailyPost") {
        "AI-AGENTS-AgentScheduler"
    }
    else {
        $TaskName
    }

    $action = New-ScheduledTaskAction -Execute $pythonExe -Argument ('"{0}" --run-scheduled' -f $mainScript)
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1)
    $trigger.RepetitionInterval = "PT1M"
    $trigger.RepetitionDuration = "P1D"

    Register-ScheduledTask -TaskName $schedulerTaskName -Action $action -Trigger $trigger -Description "AI AGENTS per-agent scheduler" -Force | Out-Null

    Write-Output "Task '$schedulerTaskName' created/updated."
    Write-Output "Schedule: every minute"
    Write-Output "Execute: $pythonExe"
    Write-Output "Arguments: \"$mainScript\" --run-scheduled"
    return
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
