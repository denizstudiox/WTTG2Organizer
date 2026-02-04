@echo off
cd /d "%~dp0"
REM Launch using pythonw to hide terminal
start "" pythonw app_launcher.pyw
exit

