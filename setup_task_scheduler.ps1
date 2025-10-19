# CodeDeBhai Monthly Rollover - Task Scheduler Setup
# Run this script as Administrator

Write-Host "Setting up Windows Task Scheduler for Monthly Credit Rollover..." -ForegroundColor Green

# Task details
$TaskName = "CodeDeBhai Monthly Rollover"
$TaskPath = "C:\Users\THARAN\Desktop\codedebhairemondata\flaskdeployment-main\run_monthly_rollover.bat"
$TaskDescription = "Automated monthly credit rollover system for CodeDeBhai"

# Create the scheduled task
$Action = New-ScheduledTaskAction -Execute $TaskPath
$Trigger = New-ScheduledTaskTrigger -Monthly -At 2:00AM -DaysOfMonth 1
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest

# Register the task
try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description $TaskDescription
    Write-Host "✅ Task scheduled successfully!" -ForegroundColor Green
    Write-Host "Task will run on the 1st of each month at 2:00 AM" -ForegroundColor Yellow
    
    # Show the created task
    Get-ScheduledTask -TaskName $TaskName | Format-List TaskName, State, NextRunTime
    
} catch {
    Write-Host "❌ Error creating task: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please run this script as Administrator" -ForegroundColor Yellow
}

Write-Host "`nTo manually run the task anytime, use:" -ForegroundColor Cyan
Write-Host "Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White

Write-Host "`nTo view task details:" -ForegroundColor Cyan
Write-Host "Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
