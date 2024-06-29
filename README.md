# Google Cloud Drive Terminal

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-Apache%202.0-green)

Google Cloud Drive Terminal - это командный интерфейс для взаимодействия с Google Cloud Drive, использующий библиотеку v3.

## Оглавление

- [Установка](#установка)
- [Использование](#использование)
- [Основные команды](#основные-команды)
- [Конфигурация](#конфигурация)
- [Вклад](#вклад)
- [Лицензия](#лицензия)

## Установка

1. Клонируйте репозиторий:

    ```sh
    git clone "https://github.com/DaniilSelin/GoogleCloudStorage/tree/main"
    ```

2. Перейдите в директорию проекта:

    ```sh
    cd google-cloud-drive-terminal
    ```

3. Создайте виртуальное окружение и активируйте его:

    ```sh
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate     # Windows
    ```

4. Установите зависимости (файл requirements.txt лежит в корневом каталоге проекта):

    ```sh
    pip install -r requirements.txt
    ```

5. Напишите на почту dan.selin2004@gmail.com для получения ключа. Он требуется для расшифровки и получения ВАМИ ваших данных для автоматической авторизации. Если нет желания получить мой ключ, можете через сервис Google Cloud (API & Services) создать свое приложение и получить уже его credentials (учетные данные).

6. Полученный ключ запишите в ./encryption/.env (Если пошли первым путем):

    ```sh
    ENCRYPTION_KEY=<Полученный от меня ключ>
    ```

7. В load_to_cloud классе GoogleCloudTerminal в методе `__init__()`:

    ```python
    self.credentials_path = <Путь к скачанным credentials>
    ```

## Использование

Запустите терминал, выполнив следующую команду:

```sh
python load_to_cloud.py
```

При первом запуске вам попросят предоставить приложению права, что необходимо сделать. В ответ на это в каталоге `<путь к проекту>/encryption/` появится файл token.json, который в дальнейшем будет использоваться для автоматической авторизации. Этот файл не рекомендуется куда-либо отправлять или выкладывать, так как он дает полный доступ к вашему гугл-диску, что может привести к утечке данных.

## Основные команды

```sh
touch: Создание файла
mkdir: Создание директории
rm: Удаление файла или директории
cp: Копирование файла или директории
cp ./source/path ./destination/path
mv: Перемещение файла или директории
mv ./source/path ./destination/path
cd: Смена текущей директории
ls: Список файлов и директорий
mimeType: Информация о расширениях и mimeType для Google
```

У каждой команды есть параметр --help:

```sh
MyDrive/ $ rm --help
usage: load_to_cloud.py [-h] [-r] [-v] [-i] [path]

Remove file from source to destination.

positional arguments:
  path               Path file that needs delete.

options:
  -h, --help         show this help message and exit
  -r, --recursive    Recursively delete the contents of the directory.
  -v, --verbose      Show information about remove files.
  -i, --interactive  Prompt before every removal.
```

## Конфигурация

Какой либо настройки проекта нет, проект настраивается автоматически.

## Вклад

Если вы хотите внести вклад в проект, пожалуйста, выполните следующие шаги:

1. Форкните репозиторий.
2. Создайте новую ветку:

    ```sh
    git checkout -b feature/your-feature-name
    ```

3. Внесите изменения и закоммитьте их:

    ```sh
    git commit -am 'Add new feature'
    ```

4. Запушьте изменения в вашу ветку:

    ```sh
    git push origin feature/your-feature-name
    ```

5. Создайте Pull Request.

## Лицензия

Этот проект лицензирован под Apache License 2.0 - подробности см. в файле LICENSE.
