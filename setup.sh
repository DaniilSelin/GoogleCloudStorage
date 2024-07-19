#!/bin/bash

# Функция для проверки есть ли Python
check_python() {
    if command -v python3 &>/dev/null; then
        echo "Python3 is already installed. Start setup"
    else
        echo "Python3 is not installed. Please install Python3..."
        exit 1
    fi
}

check_python

# Создаем виртуальное окружение
python3 -m venv env

# Активируем виртуальное окружение
source env/bin/activate

# Обновляем pip и устанавливаем зависимости
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete. To activate the virtual environment, run 'source env/bin/activate'."
