@echo off

rem blender path
set BLENDER_PYTHON=C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\bin
set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.3

set PATH=%PATH%;%BLENDER_PATH%;%BLENDER_PYTHON%;
set USER_PYTHONPATH=C:\Users\okita\AppData\Roaming\Python\Python311\site-packages

set PYTHONPATH=%PYTHONPATH%;%USER_PYTHONPATH%

rem echo %PATH%


rem call %BLENDER_PYTHON%\python.exe -V

rem call %BLENDER_PYTHON%\python.exe -m ensurepip
rem call %BLENDER_PYTHON%\python.exe -m pip install --upgrade pip

rem call "%BLENDER_PYTHON%\python.exe" -m pip install pandas --no-warn-script-location
rem call "%BLENDER_PYTHON%\python.exe" -m pip install pillow --no-warn-script-location
rem call "%BLENDER_PYTHON%\python.exe" -m pip install simpy --no-warn-script-location
rem call "%BLENDER_PYTHON%\python.exe" -m pip install sympy --no-warn-script-location
rem call %BLENDER_PYTHON%\python.exe -m pip list

echo %BLENDER_PATH%\blender.exe

rem call "%BLENDER_PATH%\blender.exe" -b -P blender_test.py
call "%BLENDER_PATH%\blender.exe" -P blender_3D.py
rem コマンドプロンプトを終了
exit /B 0