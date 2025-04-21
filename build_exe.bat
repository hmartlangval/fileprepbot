@echo off
echo Building masterapp executable...
pyinstaller --clean appstart.spec
echo Build completed. Check the dist folder for the executable.
pause 