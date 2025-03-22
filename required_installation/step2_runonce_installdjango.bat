@echo off

echo requires internet to install...
echo installing Django...

pip install Django
if %errorlevel% equ 0 (
	echo Django installed sucessfully!
) else (
	echo Failed to install Django.
Check your Python and pip setup.
)
pause