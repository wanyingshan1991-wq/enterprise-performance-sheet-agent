@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Please install Python 3.10+ or ask Codex to run setup_check.bat.
  pause
  exit /b 1
)

set "DWS_EXE=C:\Users\Administrator\.dws\data\backups\v1.0.50-20260714-093740\binary\dws.exe"
if not exist "%DWS_EXE%" (
  where dws >nul 2>nul
  if errorlevel 1 (
    echo dws CLI was not found. Please authorize DingTalk DWS first.
    pause
    exit /b 1
  )
)

python "scripts\qtu_menu.py"

echo.
pause
