@echo off
cd /d "%~dp0"
if exist "reports\report.html" (
  start "" "%~dp0reports\report.html"
  exit /b 0
)
echo Run run-tests.bat to generate a report.
pause
exit /b 1
