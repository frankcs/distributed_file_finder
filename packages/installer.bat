@echo off
echo Preparing environment
path C:/Python32/
echo Added %path% to path
echo Ready to install
pause
cd "For SetupTools"
python distribute_setup.py
cd "../argh-0.15.1"
python setup.py install
cd "../pathtools-0.1.2"
python setup.py install
cd "../PyYAML-3.10"
python setup.py install
cd "../my fixes to watchdog-0.6.0"
python setup.py install
cd "../Pyro4-4.15"
python setup.py install
cd "../PyQT"
start PyQt-Py3.2-x86-gpl-4.9-1.exe
echo.
echo If you succesfully installed PyQT it's all done
pause