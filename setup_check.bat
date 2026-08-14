@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"

echo [1/4] Checking Python
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Please install Python 3.10 or newer.
) else (
  python --version
)

echo.
echo [2/4] Checking dws CLI
set DWS_EXE=C:\Users\Administrator\.dws\data\backups\v1.0.50-20260714-093740\binary\dws.exe
if exist "%DWS_EXE%" (
  "%DWS_EXE%" --help >nul
) else (
  where dws >nul 2>nul
  if errorlevel 1 (
    echo dws CLI was not found. Ask WorkBuddy/Codex to enable DingTalk DWS.
  ) else (
    dws --help >nul
    echo dws found in PATH
  )
)

echo.
echo [3/4] Checking DingTalk authorization
if exist "%DWS_EXE%" (
  "%DWS_EXE%" profile list --format json
) else (
  dws profile list --format json
)

echo.
echo [4/4] Checking config
if exist "config\config.json" (
  echo Found config\config.json
) else (
  echo config\config.json was not found. Run first_time_setup.bat or start the tool once.
)

echo.
pause
