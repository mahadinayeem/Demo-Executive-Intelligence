@echo off
title National Geospatial Intelligence Map Engine
echo =====================================================================
echo   STARTING STANDALONE EXECUTIVE GEOSPATIAL MAP SUITE
echo =====================================================================
echo.
echo Launching local HTTP server on http://localhost:8080 ...
echo.
start http://localhost:8080/index.html
python -m http.server 8080
pause
