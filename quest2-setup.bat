@echo off
echo ============================================
echo Quest 2 Network Setup for ECG Backend
echo ============================================
echo.
echo This script will:
echo 1. Add Windows Firewall rule for port 5000
echo 2. Display your PC's IP address
echo.
echo IMPORTANT: Run this as Administrator!
echo.
pause

echo.
echo Adding Windows Firewall rule for port 5000...
netsh advfirewall firewall add rule name="Flask ECG Backend" dir=in action=allow protocol=TCP localport=5000

echo.
echo ============================================
echo Your PC's IP Address (use this in Unity):
echo ============================================
ipconfig | findstr /C:"IPv4"

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. In Unity, set Backend URL to: http://10.32.86.82:5000
echo 2. Start Flask backend: python ecg_api.py
echo 3. Build and deploy to Quest 2
echo.
pause
