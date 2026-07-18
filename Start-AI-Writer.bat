@echo off
title LOPINUZE AI Auto-Writer
echo ===================================================
echo   LOPINUZE AI Article Generator
echo   Running in Continuous Background Mode
echo ===================================================
echo.
echo The AI is now scanning for news and writing articles.
echo Leave this window open. It will write new articles every 15 minutes.
echo.
node pipeline.js --watch
pause
