@echo off
echo Starting gesture recognition test...
echo.

cd /d "%~dp0"

C:\Users\iluxa\AppData\Local\Programs\Python\Python314\python.exe test_gesture.py

if errorlevel 1 (
    echo.
    echo ERROR: Test failed!
    echo.
)

echo.
echo Press any key to close...
pause > nul
