@echo off

:: Чекаем виртуальное окружение
if not exist "env" (
    echo Virtual environment not found. Please run setup.bat first.
    exit /b 1
) else (
    set VENV_DIR=venv
)

::Провяем активировано ли виртуальное окружение
if "%VIRTUAL_ENV%"=="" (
    echo Virtual environment is not activated.
) else (
    echo Virtual environment is activated: %VIRTUAL_ENV%
)


:: Активируем оркужение
call env\Scripts\activate

python3 ./TERMINAL/GoogleCloudTerminal.py

:: Деактивируем окружение
deactivate
