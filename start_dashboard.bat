@echo off
title Ispahani Tea Limited - Executive Intelligence Portal
color 0A

echo ===============================================================================
echo       ISPAHANI TEA LIMITED -- C-SUITE EXECUTIVE INTELLIGENCE PORTAL
echo ===============================================================================
echo.
echo  [1/2] Starting Local High-Speed Analytics Server on port 8765...
start /b python -m http.server 8765 > nul 2>&1

echo  [2/2] Launching Executive Dashboard in your Default Web Browser...
timeout /t 1 > nul
start http://localhost:8765/index.html

echo.
echo ===============================================================================
echo  Dashboard is Live at: http://localhost:8765/index.html
echo  To exit, simply close this window.
echo ===============================================================================
echo.
pause
