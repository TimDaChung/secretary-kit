@echo off
title Slack Secretary
cd /d "%USERPROFILE%\.claude"
claude --model sonnet "onduty"
set EC=%errorlevel%
echo [%date% %time%] claude exited with code %EC% >> "%USERPROFILE%\.claude\secretary-exit.log"
echo claude exited with code %EC%
pause
