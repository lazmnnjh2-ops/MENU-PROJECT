@echo off
title ITNE352 Recipe Discovery Hub

echo Starting Server...
start "" cmd /k python "C:\Users\Ali\Desktop\MENU PROJECT\server.py"

timeout /t 2 >nul

echo Starting GUI Client...
start "" cmd /k python "C:\Users\Ali\Desktop\MENU PROJECT\gui.py"

exit