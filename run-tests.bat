@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Create .venv and install requirements.txt first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pytest %*
set "runExitCode=%errorlevel%"
if exist "reports\report.html" start "" "%~dp0reports\report.html"
echo Exit code: %runExitCode%
if "%~1"=="" pause
exit /b %runExitCode%
