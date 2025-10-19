@echo off
REM Monthly Credit Rollover System - Windows Task Scheduler Script
REM This script runs the production rollover system automatically

REM Change to the project directory
cd /d "C:\Users\THARAN\Desktop\codedebhairemondata\flaskdeployment-main"

REM Log the start time
echo [%DATE% %TIME%] Starting Monthly Credit Rollover System >> rollover_scheduler.log

REM Run the production rollover system
python production_rollover_system.py >> rollover_scheduler.log 2>&1

REM Log completion
echo [%DATE% %TIME%] Monthly Credit Rollover System completed >> rollover_scheduler.log
echo ===================================== >> rollover_scheduler.log

REM Optional: Send email notification (uncomment if needed)
REM python -c "import smtplib; print('Rollover completed')"

exit /b 0
