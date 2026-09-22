@echo off
title Slack Secretary
cd /d "%USERPROFILE%\.claude"

rem 模型讀 skills\secretary\config.json 的 model.session;讀不到/沒設/檔案壞掉 -> sonnet
rem 注意:for /f 反引號內的 | 不可跳脫成 ^|,否則 PowerShell 收到字面 ^ 會解析失敗並靜默 fallback
rem 想換模型改 config.json 即可,不用動這支 bat
set "MODEL=sonnet"
for /f "usebackq delims=" %%M in (`powershell -NoProfile -Command "try{$m=(Get-Content '%USERPROFILE%\.claude\skills\secretary\config.json' -Raw -Encoding UTF8 | ConvertFrom-Json).model.session; if($m){$m}else{'sonnet'}}catch{'sonnet'}"`) do set "MODEL=%%M"

echo [secretary] model = %MODEL%
claude --model %MODEL% "onduty"
set EC=%errorlevel%
echo [%date% %time%] claude exited with code %EC% (model=%MODEL%) >> "%USERPROFILE%\.claude\secretary-exit.log"
echo claude exited with code %EC%
pause
