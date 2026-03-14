```batch
@echo off
REM === Version modifiée qui se cache elle-même ===

if "%1"=="HIDDEN" goto :launch

REM Se relance en mode caché via mshta
mshta vbscript:CreateObject("WScript.Shell").Run("""%~f0"" HIDDEN",0,False)(window.close)
exit /b

:launch
REM === CODE PRINCIPAL ===
cd /d "C:\amgsbsfax-web"
call venv\Scripts\activate.bat

REM Lance Flask en arrière-plan
start /b python run.py

REM Attend que Flask démarre
timeout /t 3 /nobreak >nul

REM Ouvre le navigateur
start "" http://127.0.0.1:5003/

REM Garde le processus actif (important!)
cmd /k
```
