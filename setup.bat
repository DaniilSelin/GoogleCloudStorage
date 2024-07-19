@echo off

:: Проверяем есть ли вообще питон
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Installing Python...
) else (
    echo Python is already installed. Start setup...
)

:: Создаем виртуальное окружение куда пихаем все нужны библиотек
python -m venv env

call env\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirementsW.txt

echo Setup complete. To activate the virtual environment, run "env\Scripts\activate".
pause