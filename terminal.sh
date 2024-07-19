#!/bin/bash

# Чекаем виртуальное окружение
if [ ! -d "venv"] && [! -d "env"]; then
    echo "Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Активируем виртуальное окружение
if [ -d "venv" ]; then
    . venv/bin/activate
elif [ -d "env" ]; then
    . env/bin/activate
else
    echo "No virtual environment found. Please run setup.sh first."
    exit 1
fi

# активируем окружение
source env/bin/activate

# запускаем терминал
python3 ./TERMINAL/GoogleCloudTerminal.py

deactivate