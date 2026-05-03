@echo off
chcp 65001 >nul
for %%i in ("%~dp0") do set DIR=%%~si
set PY="C:\Users\lenovo\AppData\Local\Programs\Python\Python312\python.exe"
set GAME=%DIR%fish_game.py
echo ==============================
echo     Big Fish Game - Starting...
echo ==============================
%PY% %GAME%
if errorlevel 1 (
    echo Error! Press any key to exit...
    pause >nul
)