@echo off
cd /d "%~dp0"
py -3 neptun_watcher.py --interval 60 --open-on-up
pause
