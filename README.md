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

3. Запустите установщик в зависимости от ОС:

    ```sh
    sh setup.sh  # Linux/macOS
    cmd /c setup.bat     # Windows
    ```

4. Напишите на почту dan.selin2004@gmail.com для получения ключа. Он требуется для расшифровки и получения ВАМИ ваших данных для автоматической авторизации. Если нет желания получить мой ключ, можете через сервис Google Cloud (API & Services) создать свое приложение и получить уже его credentials (учетные данные).

5. Полученный ключ запишите в ./encryption/.env (Если пошли первым путем):

    ```sh
    ENCRYPTION_KEY=<Полученный от меня ключ>
    ```

6.2. Если вы создавали свое приложение, в GoogleCloudTerminal.py в классе GoogleCloudTerminal в методе `__init__()`:

    ```python
    self.credentials_path = <Путь к скачанным credentials>
    ```

## Использование

Запустите терминал, выполнив следующую команду:

```sh
sh terminal.sh
```

 При первом запуске вам попросят предоставить приложению права, что необходимо сделать. В ответ на это в каталоге `<путь к проекту>/TERMINAL/encryption/` появится файл token.json, который в дальнейшем будет использоваться для автоматической авторизации. Этот файл не рекомендуется куда-либо отправлять или выкладывать, так как он дает полный доступ к вашему гугл-диску, что может привести к утечке данных.

## Основные команды

```sh
touch: Создание файла
mkdir: Создание директории
rm: Удаление файла или директории
cp: Копирование файла или директории
mv: Перемещение файла или директории
cd: Смена текущей директории
ls: Список файлов и директорий
mimeType: Информация о расширениях и mimeType для Google
pattern_rm: Удаленяет по регулярному выражению
ren: Переименовывает согласно perl-выражению
trash: Перемещает файл в корзину
restore: Восстанавливает файл из корзины
emptyTrash: Очищает корзину
tree: Отображает структуру каталогов в виде дерева
du: Показывает использование дискового пространства файлами
share: Управление доступом к файлам и папкам
quota: Получение информации о квоте дискового пространства
export: Экспортирует файлы из облака
export_format: Вариации возможных преобразований mimeType для экспорта
ChangeMime: Меняет MIME-тип файла
upload: Загружает файлы в облако
sync: Синхронизирует локальную/облачную директория с облачной/локальной директорией
refresh_completer: Обновляет автодополнения.
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

Вся настройка работы происходит в файле .env, там есть три важные переменные, которые надо установить перед запуском терминала:
 PROJECT_LOGGING_PATH, ENCRYPTION_KEY, COMPLETER
Назначение первых двух очевидны, третья же нужна для того, чтобы вклюяать (1) и выключать (0) автодополнения, подготовка которых анимает некоторое время.

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
