@echo off

rem メモ帳を起動
set BLENDER_PATH="C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"

call %BLENDER_PATH% -b  -P blender_test.py

rem コマンドプロンプトを終了
exit /B 0