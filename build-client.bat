@echo off
:start
set OLD_CD=%cd%
:detect
cls
title "Detecting Python Version"
if exist %localappdata%\programs\python\python311\ (
	set py_dir="%localappdata%\programs\python\python311"
	goto install
)
if exist C:\python311\ (
	set py_dir="C:\python311"
	goto install
)
if exist %localappdata%\programs\python\python310\ (
	set py_dir="%localappdata%\programs\python\python310"
	goto install
)
if exist C:\python310\ (
	set py_dir="C:\python310"
	goto install
)
if exist %localappdata%\programs\python\python39\ (
	set py_dir="%localappdata%\programs\python\python39"
	goto install
)
if exist C:\python39\ (
	set py_dir="C:\python39"
	goto install
)
if exist %localappdata%\programs\python\python38\ (
	set py_dir="%localappdata%\programs\python\python38"
	goto install
)
if exist C:\python38\ (
	set py_dir="C:\python38\"
	goto install
)
if exist %localappdata%\programs\python\python37\ (
	set py_dir="%localappdata%\programs\python\python37"
	goto install
)
if exist C:\python37\ (
	set py_dir="C:\python37\"
	goto install
)
if exist %localappdata%\programs\python\python36\ (
	set py_dir="%localappdata%\programs\python\python36"
	goto install
)
if exist C:\python36\ (
	set py_dir="C:\python36\"
	goto install
)
if exist %localappdata%\programs\python\python35\ (
	set py_dir="%localappdata%\programs\python\python35"
	goto install
)
if exist C:\python35\ (
	set py_dir="C:\python35\"
	goto install
)
if exist %localappdata%\programs\python\python34\ (
	set py_dir="%localappdata%\programs\python\python34"
	goto install
)
if exist C:\python34\ (
	set py_dir="C:\python34\"
	goto install
)
if exist %localappdata%\programs\python\python33\ (
	set py_dir="%localappdata%\programs\python\python33"
	goto install
)
if exist C:\python33\ (
	set py_dir="C:\python33\"
	goto install
)
if exist %localappdata%\programs\python\python32\ (
	set py_dir="%localappdata%\programs\python\python32"
	goto install
)
if exist C:\python32\ (
	set py_dir="C:\python32\"
	goto install
)
if exist %localappdata%\programs\python\python31\ (
	set py_dir="%localappdata%\programs\python\python31"
	goto install
)
if exist C:\python31\ (
	set py_dir="C:\python31\"
	goto install
)
if exist %localappdata%\programs\python\python30\ (
	set py_dir="%localappdata%\programs\python\python30"
	goto install
)
if exist C:\python30\ (
	set py_dir="C:\python30\"
	goto install
)
:install
cls
title Installing Pip Modules
%py_dir%\scripts\pip install -r client-requirements.txt
%py_dir%\scripts\pip3 install -r client-requirements.txt
%py_dir%\py -m pip install -r client-requirements.txt
%py_dir%\py -m pip3 install -r client-requirements.txt
%py_dir%\python -m pip install -r client-requirements.txt
%py_dir%\python -m pip3 install -r client-requirements.txt
%py_dir%\python3 -m pip install -r client-requirements.txt
%py_dir%\python3 -m pip3 install -r client-requirements.txt

%py_dir%\scripts\pip install -r build-requirements.txt
%py_dir%\scripts\pip3 install -r build-requirements.txt
%py_dir%\py -m pip install -r build-requirements.txt
%py_dir%\py -m pip3 install -r build-requirements.txt
%py_dir%\python -m pip install -r build-requirements.txt
%py_dir%\python -m pip3 install -r build-requirements.txt
%py_dir%\python3 -m pip install -r build-requirements.txt
%py_dir%\python3 -m pip3 install -r build-requirements.txt
:build
cls
title Building EXE
echo Using %py_dir% as python directory
cd "%py_dir%\scripts"
.\pyinstaller.exe --noupx --clean --onefile --noconfirm --windowed --log-level INFO --add-data "%py_dir%\lib\site-packages\requests;requests" --add-data "%py_dir%\lib\site-packages\pillow;pillow" "%OLD_CD%\main.py"
:clean
cls
title Cleaning Up
rmdir .\build /s /q
del .\main.spec /f
move .\dist\main.exe %OLD_CD%\Client.exe
rmdir /q .\dist
:end
cls
title Build done
start msg %username% Build Done! Final build is located at: %OLD_CD%\Client.exe