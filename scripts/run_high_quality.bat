@echo off
set RESOLUTION=3280x2464
set QUALITY=95
set OUTPUT=pasta-pesto

python -m src.capture_aruco_configured --output-dir %OUTPUT% --resolution %RESOLUTION% --quality %QUALITY%
