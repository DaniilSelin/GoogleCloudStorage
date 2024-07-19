@echo off

:: Чекаем виртуальное окружение
if not exist "env" (
    echo Virtual environment not found. Please run setup.bat first.
    exit /b 1
) else (
    set VENV_DIR=venv
)

:: Активируем оркужение
call env\Scripts\activate

:: Если папку штормило по папкам, то просто сюда запихай текущий путь
:: Но учти, что надо и строчку выше поменять, чтобы окружение не создалось в текущей директории
python3 ./TERMINAL/GoogleCloudTerminal.py

:: Деактивируем окружение
deactivate
