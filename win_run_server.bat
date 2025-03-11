@echo off

echo Pathing the project
cd /d "project"

echo Activating virtual environment...
call ..\venv\scripts\activate

echo Starting Document developement server...
start cmd /k "python manage.py runserver"

echo Waiting for server to start...
timeout /t 5 >nul

echo Opening Django site in default browser...
start http://localhost:8000/admin/

pause