@echo off
REM Sri Vengamamba Food Court Launcher
REM This file starts the application without showing console window

REM Hide console window
if not "%1"=="am_admin" (powershell start -verb runAs '%0' am_admin & exit /b)

REM Start the application
start "" "SriVengamambaFoodCourt.exe"

REM Exit without showing console
exit
