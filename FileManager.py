import requests
import re
import os
import json
from google.oauth2.credentials import Credentials
from PathNavigator import PathNavigator
from UserInterface import UserInterface


class BiDict:
    """ Структура данных чем то похожая на  би-биектное отображение,
        Ныжна для взаимного отображения mimeType и расширения"""
    forward = {
        # Документы Google
        "application/vnd.google-apps.document": ".gdoc",
        "application/vnd.google-apps.spreadsheet": ".gsheet",
        "application/vnd.google-apps.presentation": ".gslides",
        "application/vnd.google-apps.form": ".gform",
        "application/vnd.google-apps.drawing": ".gdraw",
        "application/vnd.google-apps.map": ".gmap",

        # Другие файлы Google
        "application/vnd.google-apps.site": ".gsite",
        "application/vnd.google-apps.script": ".gsheet",
        "application/vnd.google-apps.fusiontable": ".gtable",
        "application/vnd.google-apps.jam": ".jam",
        "application/vnd.google-apps.shortcut": ".shortcut",

        #Файлы других форматов
        "application/vnd.google-apps.folder": "",
        "application/octet-stream": ".bin",
        "text/plain": ".txt",
        "image/jpeg": ".jpeg",
        "image/png": ".png",
        "image/gif": ".gif",
        "video/mp4": ".mp4",
        "video/x-msvideo": ".avi",
        "audio/mpeg": ".mp3",
        "audio/x-wav": ".wav",
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
        "application/zip": ".zip"
    }
    # Extension -> mimeType
    backward = {
        ".gdoc": "application/vnd.google-apps.document",
        ".gsheet": "application/vnd.google-apps.spreadsheet",
        ".gslides": "application/vnd.google-apps.presentation",
        ".gform": "application/vnd.google-apps.form",
        ".gdraw": "application/vnd.google-apps.drawing",
        ".gmap": "application/vnd.google-apps.map",
        ".gsite": "application/vnd.google-apps.site",
        ".gsheet": "application/vnd.google-apps.script",
        ".gtable": "application/vnd.google-apps.fusiontable",
        ".jam": "application/vnd.google-apps.jam",
        ".shortcut": "application/vnd.google-apps.shortcut",
        "": "application/vnd.google-apps.folder",
        ".bin": "application/octet-stream",
        ".txt": "text/plain",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".mp4": "video/mp4",
        ".avi": "video/x-msvideo",
        ".mp3": "audio/mpeg",
        ".wav": "audio/x-wav",
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".zip": "application/zip"
    }

    @staticmethod
    def add(key, value):
        if key in BiDict.forward or value in BiDict.backward:
            raise ValueError("Duplicate key or value")
        BiDict.forward[key] = value
        BiDict.backward[value] = key

    @staticmethod
    def get_by_mimeType(key, called_directly=True):
        try:
            return BiDict.forward[key]
        except KeyError:
            if called_directly:
                UserInterface.show_message(
                    [
                        {"text": "This mimeType is not extension", "color": "red"},
                        {"text": "Extensions mimeType: ", "color": "bright_yellow", "clear": "\n"}
                    ]
                )
                PathNavigator.get_mime_description()
            else:
                return None

    @staticmethod
    def get_by_extension(value, called_directly=True):
        try:
            return BiDict.backward.get(value)
        except KeyError:
            if called_directly:
                UserInterface.show_message(
                    [
                        {"text": "This extension is not extension", "color": "red"},
                        {"text": "Extensions extension: ", "color": "bright_yellow", "clear": "\n"}
                    ]
                )
                PathNavigator.get_mime_description()
            else:
                return None

    def __repr__(self):
        return f'BiDict(mimeType<->Extension)'


class ResponseTeg:
    """ Имммитация ответа от сервера """
    def __init__(self, text, status_code):
        self.text_response = text
        self.status_code_response = status_code

    @property
    def text(self):
        return self.text_response

    @property
    def status_code(self):
        return self.status_code_response


class FileManager:
    """
    Класс для работы с файлами.

    Этот класс содержит все методы, которыми пользователь оперирует во время работы.
    """

    @staticmethod
    def _creds():
        """ Восстанваливаем объект после сериализаци """
        return Credentials.from_authorized_user_info(
            json.loads(os.getenv("GOOGLE_CLOUD_CREDS")))

    @staticmethod
    def get_user_drive_id():
        """
        Не предпологает использованием польователем напрямую.
        Функция для получения идентификатора драйвера пользователя.
        Этот идентификатор используется почти во всез функциях!

        Returns:
            str: Идентификатор MyDrive.
        """
        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/json'
        }

        url = 'https://www.googleapis.com/drive/v3/files/root'
        params = {
            'fields': 'id'
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            root_drive_id = response.json().get('id')
            return root_drive_id

        except requests.exceptions.RequestException as e:
            UserInterface.show_error(
                f"Error while retrieving user drive ID: {e}"
            )
            return None

    @staticmethod
    def get_list_of_files(called_directly=True):
        """
        Не предпологает использованием польователем напрямую.
        Функция для получения списка файлов Google Drive API v3.

        Args:
            creds (Credentials): Учетные данные для аутентификации в Google API.
            called_directly (bool, optional): Флаг, указывающий, была ли функция вызвана напрямую пользователем.
                                             По умолчанию True.

        Returns:
            list: Список файлов Google Drive.
                  Возвращает None в случае ошибки.
        """
        # Создаем заголовок с авторизационным токеном
        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}'
        }

        # URL запроса для получения списка файлов Google Drive API v3
        url = 'https://www.googleapis.com/drive/v3/files'

        # Параметры запроса
        params = {
            "corpora": "user",
            'fields': 'files(name, id, mimeType, parents, size)',
        }

        # Отправляем GET-запрос к API Google Drive
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Вызываем исключение в случае ошибки HTTP

            files = response.json().get('files', [])

            if called_directly:
                if not files:
                    UserInterface.show_message('Your google drive is empty')
                else:
                    UserInterface.show_message('Files: ')
                    for file in files:
                        UserInterface.show_message(f'{file["name"]}:{file["id"]}')

            return files

        except requests.exceptions.RequestException as e:
            UserInterface.show_error(f'Failed to retrieve files: {e}')
            return None

    @staticmethod
    def get_file_metadata(file_id):
        """
        Получение метаданных файла по его идентификатору.

        Args:
            file_id: Идентификатор файла.

        Returns:
            dict: Метаданные файла.
        """
        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/json'
        }

        url = f'https://www.googleapis.com/drive/v3/files/{file_id}'
        params = {
            'fields': 'name, id, parents, mimeType, size'
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            UserInterface.show_error(f'Failed to get file metadata. Status code: {response.status_code}')
            return None

    @staticmethod
    def find_file_by_id(files, file_id: str, mime_type: str = None):
        """
        Функция для поиска папки по идентификатору.

        Args:
            files (list): Список файлов на Google Диске.
            folder_id (str): Идентификатор папки для поиска.

        Returns:
            str: Имя папки с заданным идентификатором или None, если не найдена.
        """
        files_list_id = []

        if mime_type:
            for file in files:
                if file['id'] == file_id and file['mimeType'] == mime_type:
                    files_list_id.append(file['id'])
        else:
            for file in files:
                if file['id'] == file_id:
                    return file['name']
        return None

    @staticmethod
    def find_file_by_name(files, name: str, mime_type: str = None):
        """
        Функция для поиска файла по имени.

        Args:
            files (list): Список файлов на Google Диске.
            name (str): Имя файла для поиска.

        Returns:
            list: список идентификаторов файлов с заданным именем или None,
                                                        если ни один файл не найден.
        """
        files_list_id = []
        if mime_type:
            for file in files:
                if file['name'] == name and file['mimeType'] == mime_type:
                    files_list_id.append(file['id'])
        else:
            for file in files:
                if file['name'] == name:
                    files_list_id.append(file['id'])

        return files_list_id if files_list_id else None

    @staticmethod
    def look_for_file(name: str = None, file_id: str = None, mime_type: str = None):
        """
        Функция для поиска файла на Google Диске по имени или идентификатору.

        Args:
            name (str, optional): Имя файла для поиска. По умолчанию None.
            file_id (str, optional): Идентификатор файла для поиска. По умолчанию None.

        Returns:
            str: Идентификатор или имя файла.
        """
        files = FileManager.get_list_of_files(called_directly=False)

        if file_id:
            file_name = FileManager.find_file_by_id(files, file_id, mime_type)
            if file_name:
                return file_name
            elif file_id == os.getenv("GOOGLE_CLOUD_MY_DRIVE_ID"):
                # Отмечаем, что дошли до корня
                return None
            else:
                UserInterface.show_error(
                    f'File with ID "{file_id}" not found.'
                )
                return None

        if name:
            file_id = FileManager.find_file_by_name(files, name, mime_type)
            if file_id:
                return file_id
            else:
                UserInterface.show_error(
                    f'File with name "{name}" not found.'
                )
                return None

    @staticmethod
    def format_size(size):
        # Преобразование размера файла в удобочитаемый формат
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"  # Если размер слишком большой

    @staticmethod
    def ls(path, pattern, show_long=False):
        """
        Отображает список файлов в указанной директории.

        Args:
            path (str): Путь к директории для отображения. Если None, используется текущая директория.
            show_long (bool): Если True, используется длинный формат отображения (выводит имя файла, его идентификатор и тип).
            pattern (str): Фильтр для вывода необходимых фалой по названию.
                            Испльзуется Unix-стиль для проверки на соответствия шаблону.
        """
        stop_loading = UserInterface.show_loading_message()

        if pattern:
            import fnmatch

        files = FileManager.get_list_of_files(called_directly=False)

        if path:
            path_parts_id = PathNavigator.validate_path(path=path, current_path=os.getenv("GOOGLE_CLOUD_CURRENT_PATH"))
        else:
            path_parts_id = os.getenv("GOOGLE_CLOUD_CURRENT_PATH")

        if not path_parts_id:
            UserInterface.show_error("Path is incorrect. ")
            stop_loading()
            return

        for file in files:
            if 'parents' in file.keys() and file['parents'][0] == path_parts_id:
                if show_long:
                    if "size" in file:
                        if pattern:
                            if fnmatch.fnmatch(file['name'], pattern):
                                UserInterface.show_message(
                                    f"{file['name']} ({BiDict.get_by_mimeType(file['mimeType'], called_directly=False)}): id:{file['id']} | mimeType:{file['mimeType']} | size:{FileManager.format_size(int(file['size']))}. "
                                )
                        else:
                            UserInterface.show_message(
                                f"{file['name']} ({BiDict.get_by_mimeType(file['mimeType'], called_directly=False)}): id:{file['id']} | mimeType:{file['mimeType']} | size:{FileManager.format_size(int(file['size']))}. "
                            )
                    else:
                        if pattern:
                            if fnmatch.fnmatch(file['name'], pattern):
                                UserInterface.show_message(
                                    f"{file['name']} ({BiDict.get_by_mimeType(file['mimeType'], called_directly=False)}): id:{file['id']} | mimeType:{file['mimeType']} | size:N/A. "
                                )
                        else:
                            UserInterface.show_message(
                                f"{file['name']} ({BiDict.get_by_mimeType(file['mimeType'], called_directly=False)}): id:{file['id']} | mimeType:{file['mimeType']} | size:N/A. "
                            )
                else:
                    if pattern:
                        if fnmatch.fnmatch(file['name'], pattern):
                            UserInterface.show_message(file['name'])
                    else:
                        UserInterface.show_message(file['name'])
        stop_loading()

    @staticmethod
    def mkdir(path, create_parents=False, start_path=None, called_directly=True):
        """
        Создает новую директорию по указанному пути.

        Args:
            path (str): Путь к новой директории.
            create_parents (bool): Если True, создаются все необходимые родительские директории.
            called_directly (bool): Вызвана ли функция напрямую пользовтателем
        """
        if path[0] != ".":
            path = './' + path
        # проигрываем анимацию загрузки
        stop_loading = UserInterface.show_loading_message()

        if create_parents:
            gather_needed = PathNavigator.gather_needed_paths(path)
            start_path, paths_to_create = gather_needed.values()
            new_paths_id = []

            while paths_to_create:
                start_path = FileManager.mkdir(paths_to_create[0], start_path=start_path)

                new_paths_id.append(start_path)
                paths_to_create.pop(0)
            stop_loading()
            return new_paths_id

        path_parts = re.sub('\n', "", path)

        path_parts = path_parts.strip("/").split("/")
        name_path = path_parts[-1]

        if start_path:
            parents_id = start_path
        else:
            path_parts = "/".join(path_parts[:-1])

            parents_id = PathNavigator.validate_path(path_parts, os.getenv("GOOGLE_CLOUD_CURRENT_PATH"))

            if not parents_id:
                UserInterface.show_error("Path is incorrect")
                stop_loading()
                return None

        # Создаем заголовок с авторизационным токеном
        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/json',
        }

        # URL запроса для получения списка файлов Google Drive API v3
        url = 'https://www.googleapis.com/drive/v3/files'

        # Проверяем есть ли в destination_id папки с таким же именем
        lst = [child['name'] for child in PathNavigator.get_child_files(parents_id)]

        while lst.count(name_path):

            name_path = f"Copy of {name_path}"

            lst = [child['name'] for child in PathNavigator.get_child_files(parents_id)]

        if called_directly:
            UserInterface.show_message(
                f"Creating path: {path}, parents path id: {parents_id}"
            )

        body = {
            "name": name_path,
            "mimeType": "application/vnd.google-apps.folder",
            'parents': [parents_id]
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            if called_directly:
                UserInterface.show_success('Create folder complete')
            stop_loading()
            return response.json()['id']
        else:
            if called_directly:
                UserInterface.show_error(f'error when creating folder: {response.status_code} - {response.text}')
            stop_loading()
            return None

    @staticmethod
    def _m_touch(path):
        """
        Обновляет время доступа к файл, НЕ СОЗДАЕТ НОВЫЙ.

        Args:
            path (str): Путь к файлу.
        """
        import datetime

        if not path:
            UserInterface.show_error("File name is not specified. ")
            return

        file_id = PathNavigator.validate_path(path,current_path=os.getenv("GOOGLE_CLOUD_CURRENT_PATH"), check_file=True)

        if not file_id:
            UserInterface.show_error("Paths is incorrect")
            return

        # Метод для обновления временных меток файла в Google Drive
        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/json'
        }

        url = f'https://www.googleapis.com/drive/v3/files/{file_id}'

        # Получаем текущее время в формате UTC без дробной части секунд
        modified_time = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'

        body = {
            'modifiedTime': modified_time
        }

        response = requests.patch(url, headers=headers, json=body)

        if response.status_code == 200:
            UserInterface.show_success("Update time complete!")
            return response.json()
        else:
            UserInterface.show_error(f'Failed to update file times. Status code: {response.status_code}: {response.text}')
            return None

    @staticmethod
    def touch(path, mimeType, time_modification, verbose=False):
        """
        Создает новую директорию по указанному пути.

        Args:
            path (str): Путь к новой директории.
            mimeType (str): тип объекта, используется mimeType Google Cloud
            time_modification (bool): Не создавать новый файл, а лишь обновить время доступа
            verbose (bool): Нужно ли выводить информацию о созданных файлах.
        """
        stop_loading = UserInterface.show_loading_message()

        # Словарь для выбора функции
        actions = {
            'time_modification': FileManager._m_touch,
        }

        # Найти первый истинный параметр и вызвать соответствующую функцию
        # Раньше тут было три разных функций, но из за их ненадобности я оставил только одну
        # Однако логику не решился удалять, поэтому пусть пока останется
        for action, func in actions.items():
            if locals()[action]:  # Проверить, если параметр истинный
                func(path)
                stop_loading()
                return

        path = re.sub('\n', "", path)

        path = path.strip("/").split("/")

        name_file = path[-1]

        path = "/".join(path[:-1])

        if not path:
            parents_id = os.getenv("GOOGLE_CLOUD_CURRENT_PATH")
        else:
            parents_id = PathNavigator.validate_path(path, os.getenv("GOOGLE_CLOUD_CURRENT_PATH"))

        if not parents_id:
            UserInterface.show_error("Path is incorrect")
            stop_loading()
            return None

        if not name_file:
            UserInterface.show_error("Ur forgot give me name new filee")

        # Проверяем есть ли в destination_id папки с таким же именем
        lst = [child['name'] for child in PathNavigator.get_child_files(parents_id)]

        while lst.count(name_file):
            UserInterface.show_message(
                [{"text": f"Name: {name_file} is occupied. ", "color": "bright_yellow"}]
            )
            name_file = f"Copy of {name_file}"
            UserInterface.show_message(f"I'll try to create a file named '{name_file}'. ")
            lst = [child['name'] for child in PathNavigator.get_child_files(parents_id)]

        # Метод для создания файла в Google Cloud
        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/json'
        }

        url = f'https://www.googleapis.com/drive/v3/files'

        body = {
            "name": name_file,
            'parents': [parents_id]
        }

        if mimeType:
            body["mimeType"] = mimeType

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            if verbose:
                UserInterface.show_success(
                    f"Creating file complete! file: name <{response.json()['name']}>, id <{response.json()['id']}>"
                )
            else:
                UserInterface.show_success("Creating file complete!")
            stop_loading()
            return response.json()
        else:
            UserInterface.show_error(f'Failed then create file. Status code: {response.status_code}')
            stop_loading()
            return None

    @staticmethod
    def cp(source: str, destination: str, recursive=False, mimeType=None):
        """
        Копирует директории или файлы source в destination.

        Args:
            source (str): Путь к тому, что надо скопировать.
            destination (str): Путь куда надо скопировать.
            recursive (bool): Нужно ли копировать рекурсивно.
            mimeType (str): Сужение посика нужного файла до определенного mimeType
        """
        stop_loading = UserInterface.show_loading_message()

        source_id = PathNavigator.validate_path(source, os.getenv("GOOGLE_CLOUD_CURRENT_PATH"), check_file=True, mimeType=mimeType)
        destination_id = PathNavigator.validate_path(destination, os.getenv("GOOGLE_CLOUD_CURRENT_PATH"))
        # проверяем корректность обоих путей
        if not source_id:
            UserInterface.show_error("Source is incorrect")
            stop_loading()
            return
        if not destination_id:
            UserInterface.show_error("Destination is incorrect")
            stop_loading()
            return None

        # сначала проверим тип файла, и если он не папка, то независимо от recursive
        # копируем только этот файл
        file_source = FileManager.get_file_metadata(source_id)

        if file_source['mimeType'] == 'application/vnd.google-apps.folder' and not recursive:
            if FileManager._copy_folder(file_source, destination_id):
                UserInterface.show_success(f'Folder copied successfully to {destination}')
                stop_loading()
                return
        elif file_source['mimeType'] != 'application/vnd.google-apps.folder':
            # так как у не папки детей быть не может, а лишняя предосторожность не помешает
            if FileManager._copy_file(file_source, destination_id):
                UserInterface.show_success(f'File copied successfully to {destination}')
                stop_loading()
                return
        else:
            if FileManager._copy_directory(file_source, destination_id):
                UserInterface.show_success(f'Recursive files copied successfully to {destination}')
                stop_loading()
                return

    @staticmethod
    def _copy_folder(source, destination_id):
        """
        Не подразумевает использованием напрямую пользователем.
        Так как папку копировать нельзя, просто создаем новую.
        Копирует только директорию source в destination.

        Args:
            source (dict): field объект google drive v3..
            destination_id (str): id папки куда надо "скопировать" папку. Определяется еще в cp
        """
        # Создаем папку, так как нельз их копировать...
        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/json',
        }

        # URL запроса для получения списка файлов Google Drive API v3
        url = 'https://www.googleapis.com/drive/v3/files'

        name_copy_folder = f"Copy of {source['name']}"

        # Проверяем есть ли в destination_id папки с таким же именем
        lst = [child['name'] for child in PathNavigator.get_child_files(destination_id)]

        while lst.count(name_copy_folder):
            name_copy_folder = f"Copy of {name_copy_folder}"

            lst = [child['name'] for child in PathNavigator.get_child_files(destination_id)]

        # Если имя отсавить без изменений то у нас появиться два одинковых пути
        body = {
            "name": name_copy_folder,
            "mimeType": "application/vnd.google-apps.folder",
            'parents': [destination_id]
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    @staticmethod
    def _copy_file(source, destination_id):
        """
        Не подразумевает использованием напрямую пользователем
        Копирует только файл (не директорию) source в destination.

        Args:
            source (dict): field объект google drive v3..
            destination_id (str): id папки куда надо скопировать. Определяется еще в cp
        """
        # Реализация копирования одного файла
        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/json',
        }
        url = f'https://www.googleapis.com/drive/v3/files/{source["id"]}/copy'
        body = {
            'parents': [destination_id]
        }
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            return response.json()
        else:
            UserInterface.show_error(f"Error copying file: {response.status_code} - {response.text}")
            return None

    @staticmethod
    def _copy_directory(source, destination_id):
        """
        Не подразумевает использованием напрямую пользователем
        Рекурсивно копирует файлы в директории source в destination.

        Args:
            source (dict): field объект google drive v3..
            destination_id (str): id папки куда надо скопировать. Определяется еще в cp
        """
        destination_id = FileManager._copy_folder(source, destination_id)['id']

        needed_copy = PathNavigator.gather_structure(source['id'])

        iterator = iter(needed_copy)

        # использую стандартный итератор для фикса проблемы с извлечением следующего элемента при "?"
        for file in iterator:

            if file == "!":
                next_file = next(iterator, None)
                if not next_file:
                    break
                elif next_file == "?":
                    file = "?"
                else:
                    next_file = FileManager._copy_folder(next_file, destination_id)
                    destination_id = next_file['id']
                    continue

            if file == "?":
                previous_file = FileManager.get_file_metadata(destination_id)
                destination_id = previous_file['parents'][0]

            if file != '!' and file != '?':
                FileManager._copy_file(file, destination_id)
        return True

    @staticmethod
    def _remove_file(id_remove):
        """
        Не подразумевает использованием напрямую пользователем
        Удаляет ровно один файл или папку, если у неё нет дочерних файлов.

        Args:
            id_remove (str): field объект google drive v3..
        """
        if PathNavigator.get_child_files(id_remove):
            return ResponseTeg("Folder have child files", 403)

        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}'
        }

        # URL запроса для удаления файла Google Drive API v3
        url = f'https://www.googleapis.com/drive/v3/files/{id_remove}'

        response = requests.delete(url, headers=headers)

        return response

    @staticmethod
    def _recursive_remove_branch(verbose, interactive, remove_files_struct):
        """
        Рекурсивно удаляет файлы директорию.

        Args:
            remove_files_struct (list): Результат метода PathNavigator.gather_structure()
                                            Список обьектов field Google Drive v3
                                            Содержит всю ветку начиная с директории, которую нужно рекурсивно удалить
                                            САМ КОРЕНЬ ВЕТКИ НЕ СОДЕРЖИТ
            verbose (bool): Выводить ли дополнительную информацию, о этапах рекусривного удаления файла.
            interactive (bool): Запрашивать согласие перед каждым удалением файла, в случае отказа, файл не будет удлён.
        """
        remove_files_struct = iter(remove_files_struct[::-1])

        for file_remove in remove_files_struct:
            response = None

            # пропускаем все сигналы ! и ?
            while isinstance(file_remove, str):
                file_remove = next(remove_files_struct, None)

            if not file_remove:
                break

            if verbose:
                try:
                    rfile_mime = BiDict.get_by_mimeType(file_remove['mimeType'])
                    UserInterface.show_message(f"I'll trying delete: {file_remove['name']} ({rfile_mime}): {file_remove['id']}")
                except KeyError:
                    UserInterface.show_message(
                        [{"text": f"mimeType is not defined", "color": "bright_yellow"}]
                    )
                    UserInterface.show_message(f"I'll trying delete: {file_remove['name']} (None): {file_remove['id']}")

            if interactive:
                if FileManager._confirm_action(file_remove['name']):
                    UserInterface.show_message("The action is confirmed. We continue the execution. ")
                    response = FileManager._remove_file(file_remove['id'])
                else:
                    UserInterface.show_message("The action has been canceled. ")
                    continue
            else:
                response = FileManager._remove_file(file_remove['id'])

            if response.status_code == 204:
                UserInterface.show_success(f"{file_remove['name']} delete complete")
            else:
                UserInterface.show_error(f'error when deleting file: {response.status_code} - {response.text}')

    @staticmethod
    def _confirm_action(name_file):
        """
        Запрашивает подтверждение действия у пользователя.

        Args:
            name_file (str): Имя файла, над которым будет производиться действие.
        """
        while True:
            response = input(f"Are you sure you want to delete this file (y/n): ").strip().lower()
            if response in ('yes', 'y'):
                return True
            elif response in ('no', 'n'):
                return False
            else:
                UserInterface.show_message(
                    [{"text": f"Please enter 'yes' or 'no' to confirm. ", "color": "bright_yellow"}]
                )

    @staticmethod
    def pattern_rm(path_pattern, recursive, verbose, interactive, mimeType):
        """
        Удаляет директорию или файл, путь к которму path.

        Args:
            path (str): Путь к тому, что надо удалить.
            verbose (bool): Выводить ли дополнительную информацию, о этапах удаления файла.
            interactive (bool): Запрашивать согласие перед каждым удалением файла, в случае отказа, файл не будет удлён.
            recursive (bool): Каскадное удаление файлов в path.
            mimeType (str): Сужение посика нужного файла до определенного mimeType
            RGE (bool): Реквием голден экспириенс, мы откатываем паттерны назад
        """
        stop_loading = UserInterface.show_loading_message()
        import fnmatch
        # ЭТАП подготовки списка фалов - кандидатов на удлаения
        delete_pattern = []

        path_pattern = re.sub('\n', "", path_pattern)

        path_pattern = path_pattern.strip("/").split("/")

        if path_pattern[-1][0] == "{":
            pattern_result = path_pattern[-1][1:-1]
        else:
            pattern_result = path_pattern[-1]

        files = FileManager.get_list_of_files(called_directly=False)
        # отбор кандидатов на удаления
        for file in files:
            if fnmatch.fnmatch(file['name'], pattern_result):
                delete_pattern.append(file)

        if not delete_pattern:
            UserInterface.show_error(f"File with pattern {pattern_result} not found. ")
            return

        # ЭТАП подготовки полного пути указанного полбзователем
        start_path = "./"
        # ожидаемый конечный родитель
        if path_pattern[0] == "~":
            start_path = os.getenv("GOOGLE_CLOUD_MY_DRIVE_ID")
            path_pattern.pop(0)
        else:
            start_path = os.getenv("GOOGLE_CLOUD_CURRENT_PATH")

        def handle_double_dots(current_path):
            """обработка .. в пути"""
            nonlocal start_path
            if path_pattern and path_pattern[0] == "..":
                # получаем ид родителя и удаляем .. из пути
                start_path = FileManager.get_file_metadata(current_path)['parents'][0]
                path_pattern.pop(0)
                return handle_double_dots(start_path)

        handle_double_dots(start_path)

        if path_pattern[0] == ".":
            # если требуется начать с нынешней директории
            should_parents = path_pattern
            path_pattern.pop(0)

        _path_pattern = PathNavigator.pwd(start_path)[:-1]
        _path_pattern = re.sub('\n', "", _path_pattern)
        _path_pattern = _path_pattern.strip("/").split("/")

        full_path_pattern = _path_pattern + path_pattern
        # ЭТАП фильтрации файлов выделенных под удаления
        for file in delete_pattern:
            # Убираем артефакты от каомынды pwd
            candidate = PathNavigator.pwd(file['id'])[:-1]
            candidate = re.sub('\n', "", candidate)
            candidate = candidate.strip("/").split("/")
            iterCand = iter(candidate)

            for check in full_path_pattern:
                PathOfCand = next(iterCand)

                if not PathOfCand:
                    delete_pattern.remove(file)
                    break

                if check[0] == "{":
                    if not fnmatch.fnmatch(PathOfCand, check[1:-1]):
                        delete_pattern.remove(file)
                        break
                else:
                    if PathOfCand != check:
                        delete_pattern.remove(file)
                        break

        # ЭТАП УДАЛЕНИЯ ОТБРАНЫХ ФАЙЛОВ
        for file in delete_pattern:
            candidate = PathNavigator.pwd(file['id'])[:-1]
            candidate = candidate.replace("MyDrive", "~", 1)
            UserInterface.show_message([
            {"text": f"Start process delete: {candidate}",
             'color': "bright_yellow"}
            ])
            stop_loading()
            try:
                FileManager.rm(candidate, recursive, verbose, interactive, mimeType)
            except Exception as e:
                UserInterface.show_error(f"error when deleting this file: {e}; I'm moving on to the next file")
            stop_loading = UserInterface.show_loading_message()
        stop_loading()

    @staticmethod
    def rm(path, recursive, verbose, interactive, mimeType):
        """
        Удаляет директорию или файл, путь к которму path.

        Args:
            path (str): Путь к тому, что надо удалить.
            verbose (bool): Выводить ли дополнительную информацию, о этапах удаления файла.
            interactive (bool): Запрашивать согласие перед каждым удалением файла, в случае отказа, файл не будет удлён.
            recursive (bool): Каскадное удаление файлов в path.
            mimeType (str): Сужение посика нужного файла до определенного mimeType
        """
        stop_loading = UserInterface.show_loading_message()

        id_remove = PathNavigator.validate_path(path, os.getenv("GOOGLE_CLOUD_CURRENT_PATH"), check_file=True, mimeType=mimeType)
        if not id_remove:
            stop_loading()
            return None
        file_remove_root = FileManager.get_file_metadata(id_remove)

        # папку без рекурсиваного удаления, удалять нельзя
        if file_remove_root['mimeType'] == 'application/vnd.google-apps.folder':
            remove_files_struct = PathNavigator.gather_structure(id_remove)

            if not recursive and not remove_files_struct:
                response = None

                if interactive:
                    stop_loading()
                    if FileManager._confirm_action(file_remove_root['name']):
                        stop_loading = UserInterface.show_loading_message()
                        UserInterface.show_message("The action is confirmed. We continue the execution. ")
                        response = FileManager._remove_file(id_remove)
                    else:
                        UserInterface.show_message("The action has been canceled. ")
                        return

                else:
                    if verbose:
                        UserInterface.show_message(f"I'll trying delete: {file_remove_root['name']} (folder): {file_remove_root['id']}")

                    response = FileManager._remove_file(id_remove)

                if response.status_code == 204:
                    UserInterface.show_success(f"{file_remove_root['name']} delete complete")
                    stop_loading()
                    return
                else:
                    UserInterface.show_error(f'error when deleting file: {response.status_code} - {response.text}')
                    stop_loading()
                    return

            elif recursive:
                response = None

                if verbose:
                    UserInterface.show_message([
                        {"text": f"folder ({file_remove_root['name']}) have child files, i'll try to delete them.", 'color': "bright_yellow"}
                        ])
                    UserInterface.show_message(f"I'm starting to clean the branch")

                # чистим ветку
                FileManager._recursive_remove_branch(verbose, interactive, remove_files_struct)

                if verbose:
                    UserInterface.show_message(f"I'll trying delete: {file_remove_root['name']} (folder): {file_remove_root['id']}")

                if interactive:
                    stop_loading()
                    if FileManager._confirm_action(file_remove_root['name']):
                        stop_loading = UserInterface.show_loading_message()
                        UserInterface.show_message("The action is confirmed. We continue the execution. ")
                        response = FileManager._remove_file(id_remove)
                    else:
                        UserInterface.show_message("The action has been canceled. ")
                        return
                else:
                    # удаляем корень очищенной ветки
                    response = FileManager._remove_file(id_remove)

                if response.status_code == 204:
                    UserInterface.show_success(f"{file_remove_root['name']} delete complete")
                    UserInterface.show_success(f'Recursive deletion is complete')
                    stop_loading()
                    return
                else:
                    UserInterface.show_error(f'error when deleting file: {response.status_code} - {response.text}')
                    stop_loading()
                    return
            else:
                UserInterface.show_error(f'error when deleting file: This folder have child files')
                stop_loading()
                return

        else:
            response = None

            if interactive:
                stop_loading()
                if FileManager._confirm_action(file_remove_root['name']):
                    stop_loading = UserInterface.show_loading_message()
                    UserInterface.show_message("The action is confirmed. We continue the execution. ")
                    response = FileManager._remove_file(id_remove)
                else:
                    UserInterface.show_message("The action has been canceled. ")
                    stop_loading()
                    return

            else:
                if verbose:
                    try:
                        rfile_mime = BiDict.get_by_mimeType(file_remove_root['mimeType'])
                        UserInterface.show_message(f"I'll trying delete: {file_remove_root['name']} ({rfile_mime}): {file_remove_root['id']}")
                    except KeyError:
                        UserInterface.show_message(
                            [{"text": f"mimeType is not defined", "color": "bright_yellow"}]
                        )
                        UserInterface.show_message(
                            f"I'll trying delete: {file_remove_root['name']} (None): {file_remove_root['id']}")

                response = FileManager._remove_file(id_remove)

            if response.status_code == 204:
                UserInterface.show_success(f"{file_remove_root['name']} delete complete")
                stop_loading()
                return
            else:
                UserInterface.show_error(f'error when deleting file: {response.status_code} - {response.text}')
                stop_loading()
                return

    @staticmethod
    def mv(source_path: str, destination_path: str, mimeType: str):
        """
        Перемещает source_path в destination_path.

        Args:
            source_path (str): Путь к тому, что надо переместить.
            destination_path (str): Путь куда надо переместить.
            mimeType (str): Сужение поиска нужного файла до определенного mimeType
        """
        stop_loading = UserInterface.show_loading_message()

        source_id = PathNavigator.validate_path(source_path, current_path=os.getenv("GOOGLE_CLOUD_CURRENT_PATH"), check_file=True, mimeType=mimeType)
        destination_id = PathNavigator.validate_path(destination_path, current_path=os.getenv("GOOGLE_CLOUD_CURRENT_PATH"))

        if not source_id:
            UserInterface.show_error("Source path is incorrect")
            stop_loading()
            return

        if not destination_id:
            UserInterface.show_error("Destination path is incorrect")
            stop_loading()
            return

        source_metadata = FileManager.get_file_metadata(source_id)

        if not source_metadata:
            UserInterface.show_error("Failed to retrieve source file metadata")
            stop_loading()
            return

        # Проверка метаданных родителей
        parents = source_metadata.get("parents")
        if not parents:
            UserInterface.show_error("Source file has no parent directory")
            stop_loading()
            return

        old_parent_id = parents[0]

        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/json'
        }

        url = f'https://www.googleapis.com/drive/v3/files/{source_id}'

        # Сначала добавляем нового родителя
        body = {
            'addParents': [destination_id]
        }

        response = requests.patch(url, headers=headers, json=body)

        if response.status_code != 200:
            UserInterface.show_error(f'Failed to add new parent. Status code: {response.status_code}: {response.text}')
            stop_loading()
            return None

        # Затем удаляем старого родителя
        body = {
            'removeParents': [old_parent_id]
        }

        response = requests.patch(url, headers=headers, json=body)

        if response.status_code == 200:
            UserInterface.show_success(f"Transfer is completed. File moved to new location.")
        else:
            UserInterface.show_error(f'Failed to remove old parent. Status code: {response.status_code}: {response.text}')

        stop_loading()

    @staticmethod
    def ren(perl_expression, pattern_file):
        """
        Переименовывает согласно perl-выражению файлы с именнем подходящему по pattern_file.
        По сути урезаная копия rename Perl-expression из линукса, но со сложныеми perl-выражения не работает,
            так как это требует компиляции таких perl-выражений, чего уже я не хочу
        Пример: ren 's/old/new/' old_file.txt

        Args:
            perl_expression (str): Perl-выражение.
            pattern_file (str): паттерн согласно, которому избираются файлы.
        """
        stop_loading = UserInterface.show_loading_message()

        import fnmatch
        files = PathNavigator.get_child_files(os.getenv("GOOGLE_CLOUD_CURRENT_PATH"))
        # Разделяем Perl-выражение на паттерн и замену
        try:
            pattern, replacement = perl_expression.split('/')[1:3]
        except Exception as e:
            UserInterface.show_error(f"Incorrect pattern: {e}")
            stop_loading()
            return

        # Применяем регулярное выражение
        for file in files:
            if fnmatch.fnmatch(file['name'], pattern_file):
                try:
                    file_new_name = re.sub(pattern, replacement, file['name'])
                except Exception as e:
                    UserInterface.show_error(f"Incorrect pattern: {e}")
                    continue

                if file_new_name == file['name']:
                    UserInterface.show_message(
                        [{"text": "Old and new names the same.", "color": "bright_yellow"}]
                    )
                    continue
                # обновляем имя файла
                # Метод для обновления временных меток файла в Google Drive
                headers = {
                    'Authorization': f'Bearer {FileManager._creds().token}',
                    'Content-Type': 'application/json'
                }

                url = f'https://www.googleapis.com/drive/v3/files/{file["id"]}'

                body = {
                    'name': file_new_name,
                    'fields': 'name, id'  # Указываем поля, которые хотим получить в ответе
                }

                response = requests.patch(url, headers=headers, json=body)

                if response.status_code == 200:
                    UserInterface.show_message(f"rename is completed")
                else:
                    UserInterface.show_error(
                        f'Failed to rename file. Status code: {response.status_code}: {response.text}'
                    )
        stop_loading()

    @staticmethod
    def mimeType():
        """
        Функция для вывода списка mimeType и их расширений.
        """
        for mime in PathNavigator.get_mime_description():
            UserInterface.show_message(f"{mime['mime']} ({mime['extension']}): {mime['description']}")

    @staticmethod
    def trash(path, mimeType):
        """
        Перемещает файл по пути path в корзину

        Args:
            path (str): путь к тому что надо переместить в корзину.
        """
        stop_loading = UserInterface.show_loading_message()

        file_id = PathNavigator.validate_path(
            path,
            os.getenv("GOOGLE_CLOUD_CURRENT_PATH"),
            check_file=True,
            mimeType=mimeType
        )

        if not file_id:
            UserInterface.show_error("Incorrect path. ")
            stop_loading()
            return

        # URL запроса
        url = f'https://www.googleapis.com/drive/v3/files/{file_id}'

        # Заголовки
        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/json'
        }

        # Тело запроса
        body = {
            'trashed': True
        }

        # Отправка запроса
        response = requests.patch(url, headers=headers, json=body)

        if response.status_code == 200:
            UserInterface.show_success('File moved to trash successfully.')
        else:
            UserInterface.show_error(f'Failed to move file to trash: {response.text}')
        stop_loading()

    @staticmethod
    def restore(path, mimeType):
        """
        Восстанавливает файл из корзины по пути *path.
        * - учитывается положение файла до перемещения в корзину.

        Args:
            path (str): путь к тому что надо восстановить из корзины.
        """
        stop_loading = UserInterface.show_loading_message()

        file_id = PathNavigator.validate_path(
            path,
            os.getenv("GOOGLE_CLOUD_CURRENT_PATH"),
            check_file=True,
            mimeType=mimeType
        )

        if not file_id:
            UserInterface.show_error("Incorrect path. ")
            stop_loading()
            return

        # URL запроса
        url = f'https://www.googleapis.com/drive/v3/files/{file_id}'

        # Заголовки
        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/json'
        }

        # Тело запроса
        body = {
            'trashed': False
        }

        # Отправка запроса
        response = requests.patch(url, headers=headers, json=body)

        if response.status_code == 200:
            UserInterface.show_success('File restored from trash successfully. ')
        else:
            UserInterface.show_error(f'Failed to restore file from trash: {response.text}')
        stop_loading()

    @staticmethod
    def empty_trash():
        """
        Очищает корзину
        """
        stop_loading = UserInterface.show_loading_message()
        # URL запроса
        url = 'https://www.googleapis.com/drive/v3/files/trash'

        # Заголовки
        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
        }

        # Отправка запроса
        response = requests.delete(url, headers=headers)

        if response.status_code == 204:
            UserInterface.show_success('Trash emptied successfully.')
        else:
            UserInterface.show_error(f'Failed to empty trash: {response.text}')
        stop_loading()

    @staticmethod
    def tree(path, dirs_only, no_indent, size, pattern):
        """
        Отображение структуры каталогов в виде дерева.
        Args:
            path (str): что возпринимать как окрневой католог (по умолчанию root)
            dirs_only (bool): Выводим только директории.
            no_indent (bool): Выводим чистым списком, без ветвления.
            size (bool): Выводить еще и размер.
            pattern (str): Фильтр для вывода необходимых фалой по названию.
                            Испльзуется Unix-стиль для проверки на соответствия шаблону.
        """
        if pattern:
            import fnmatch
        stop_loading = UserInterface.show_loading_message()

        if path:
            source_id = PathNavigator.validate_path(path, os.getenv("GOOGLE_CLOUD_CURRENT_PATH"), check_file=True)
        else:
            source_id = os.getenv("GOOGLE_CLOUD_CURRENT_PATH")

        if not source_id:
            UserInterface.show_error("Path is incorrect")
            stop_loading()
            return

        files = PathNavigator.gather_structure(source_id)

        iterator = iter(files)

        count_space = 0
        indent = "" if no_indent else "    "

        # использую стандартный итератор для фикса проблемы с извлечением следующего элемента при "?"
        for file in iterator:

            if file == "!":
                next_file = next(iterator, None)
                if not next_file:
                    break
                elif next_file == "?":
                    file = "?"
                else:
                    file_output = f"{count_space * indent}{next_file['name']}/"
                    if not pattern:
                        UserInterface.show_message(file_output)
                    else:
                        if fnmatch.fnmatch(next_file['name'], pattern):
                            UserInterface.show_message(file_output)

                    if not no_indent:
                        count_space += 1
                    else:
                        # улиняем путь так как поднялись на одну папку вверх
                        count_space = 1
                        if next_file["mimeType"] == 'application/vnd.google-apps.folder':
                            indent = indent + next_file['name'] + "/"
                    continue

            if file == "?":
                if not no_indent:
                    count_space -= 1
                else:
                    count_space = 1
                    # урезаем путь так как опустились на одну папку вверх
                    indent = indent[:-1]
                    i = len(indent) - 1
                    while i >= 0 and indent[i] != "/":
                        indent = indent[:-1]
                        i -= 1

            if file != '!' and file != '?':
                if no_indent:
                    count_space = 1

                if dirs_only:
                    continue

                if size:
                    if "size" in file:
                        if not pattern:
                            UserInterface.show_message(
                                [{"text": f"{count_space * indent}{file['name']} {FileManager.format_size(int(file['size']))}"}]
                            )
                        else:
                            if fnmatch.fnmatch(file['name'], pattern):
                                UserInterface.show_message(
                                    [{
                                         "text": f"{count_space * indent}{file['name']} {FileManager.format_size(int(file['size']))}"}]
                                )
                    else:
                        if not pattern:
                            UserInterface.show_message(
                                [{
                                     "text": f"{count_space * indent}{file['name']} N/A"}]
                            )
                        else:
                            if fnmatch.fnmatch(file['name'], pattern):
                                UserInterface.show_message(
                                    [{
                                        "text": f"{count_space * indent}{file['name']} N/A"}]
                                )
                else:
                    if not pattern:
                        UserInterface.show_message(
                            [{"text": f"{count_space * indent}{file['name']} "}]
                        )
                    else:
                        if fnmatch.fnmatch(file['name'], pattern):
                            UserInterface.show_message(
                                [{"text": f"{count_space * indent}{file['name']} "}]
                            )
        stop_loading()

    @staticmethod
    def du(path, all, show_free_space):
        """
        Отображение использования дискового пространства на Google Диске.

        Args:
            path (str): Путь к директории для анализа.
            dirs_only (bool): Показывать только директории.
            show_free_space (bool): Показать свободное место на Google Диске.
        """
        stop_loading = UserInterface.show_loading_message()

        if show_free_space:
            FileManager.show_free_space()
            stop_loading()
            return

        if path:
            source_id = PathNavigator.validate_path(path=path, current_path=os.getenv("GOOGLE_CLOUD_CURRENT_PATH"))
        else:
            path = './'
            source_id = os.getenv("GOOGLE_CLOUD_CURRENT_PATH")

        if not source_id:
            UserInterface.show_error("Path is incorrect")
            stop_loading()
            return

        files = PathNavigator.gather_structure(source_id)
        FileManager.display_usage(path, files, all)

        stop_loading()

    @staticmethod
    def display_usage(path, files, all):
        """
        Отображение использования дискового пространства для списка файлов/директорий.
        """
        iterator = iter(files)

        indent = ""
        total_size = [0]
        total_folders = ["main"]

        # использую стандартный итератор для фикса проблемы с извлечением следующего элемента при "?"
        for file in iterator:

            if file == "!":
                next_file = next(iterator, None)
                if not next_file:
                    break
                elif next_file == "?":
                    file = "?"
                else:
                    total_size.append(0)
                    total_folders.append(next_file)

                    if next_file["mimeType"] == 'application/vnd.google-apps.folder':
                        indent = indent + next_file['name'] + "/"
                    continue

            if file == "?":
                # урезаем путь так как опустились на одну папку вверх
                indent = indent[:-1]
                i = len(indent) - 1
                while i >= 0 and indent[i] != "/":
                    indent = indent[:-1]
                    i -= 1
                # Выводим размер текущей папки
                size = total_size.pop()
                # так как эта папка тоже поддиректория предыдущей
                total_size[-1] += size

                folder = total_folders.pop()

                result_size = FileManager.format_size(size)

                file_output = f"{result_size}{(10-len(result_size)) * ' '}|    {path}{indent}{folder['name']}/"
                UserInterface.show_message(file_output)

            if file != '!' and file != '?':
                if "size" in file:
                    total_size[-1] += int(file['size'])
                    if all:
                        result_size = FileManager.format_size(int(file['size']))
                        UserInterface.show_message([{
                            "text": f"{result_size}{(10-len(result_size)) * ' '}|    {path}{indent}{file['name']}"
                        }])
                else:
                     if all:
                         result_size = "N/A"
                         UserInterface.show_message([{
                                "text": f"{result_size}{(10-len(result_size)) * ' '}|    {path}{indent}{file['name']}"
                         }])
        # выводим размер основной ветки
        size = total_size.pop()
        result_size = FileManager.format_size(size)
        file_output = f"{result_size}{(10-len(result_size)) * ' '}|    {path}"
        UserInterface.show_message(file_output)

    @staticmethod
    def show_free_space():
        """
        Показать свободное место на Google Диске.
        """
        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}'
        }

        url = 'https://www.googleapis.com/drive/v3/about?fields=storageQuota'

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            quota = response.json()['storageQuota']
            limit = int(quota.get('limit', 0))
            usage = int(quota.get('usage', 0))
            free_space = limit - usage if limit else 'Unlimited'

            UserInterface.show_message(
                [{"text": f"Total space: {FileManager.format_size(limit)}", "color": "bright_yellow"}]
            )
            UserInterface.show_message(
                [{"text": f"Used space: {FileManager.format_size(usage)}", "color": "bright_yellow"}]
            )
            UserInterface.show_message(
                [{"text": f"Free space: {FileManager.format_size(free_space)}", "color": "bright_yellow"}]
            )
        else:
            UserInterface.show_error(
                f'Failed to retrieve free space. Status code: {response.status_code}'
            )

    @staticmethod
    def share(path, email, role, type, mimeType):
        """
        Управление доступом и настройками общего доступа к файлам и папкам.

        Args:
            path (str): Путь к файлу или папке, для которых нужно настроить доступ.
            email (str): Электронная почта пользователя, которому предоставляется доступ.
            role (str): Роль доступа ('writer', 'commenter', 'reader', 'organizer', 'fileOrganizer').
            type (str, optional): Тип доступа (по умолчанию 'user'). Может быть 'user', 'group', 'domain', 'anyone', или 'restricted'.
        """

        stop_loading = UserInterface.show_loading_message()

        source_id = PathNavigator.validate_path(path, os.getenv("GOOGLE_CLOUD_CURRENT_PATH"), check_file=True, mimeType=mimeType)
        if not source_id:
            UserInterface.show_error("Path is incorrect")
            stop_loading()
            return

        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/json'
        }

        url = f"https://www.googleapis.com/drive/v3/files/{source_id}/permissions"

        if type == 'restricted':
            # Удалить все текущие разрешения (ограничить доступ)
            current_permissions = requests.get(url, headers=headers).json().get('permissions', [])
            for permission in current_permissions:
                delete_url = f"{url}/{permission['id']}"
                requests.delete(delete_url, headers=headers)
            UserInterface.show_success("All permissions have been removed. The file is now restricted.")
            stop_loading()
            return

        body = {
            'role':  role,
            'type': type,
        }
        if email:
            body['emailAddress'] = email

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            UserInterface.show_success("Permission granted successfully")
            stop_loading()
            return response.json()
        else:
            UserInterface.show_error(
                f'Failed to grant permission. Status code: {response.status_code}: {response.text}')
            stop_loading()
            return None

    @staticmethod
    def quota():
        """
        Получение информации о квоте дискового пространства Google Drive.
        """
        stop_loading = UserInterface.show_loading_message()
        FileManager.show_free_space()
        stop_loading()

    @staticmethod
    def sync(drive_path, local_path, sync_mode="download"):
        """
        sync: Синхронизация репозитория. По факту скачивание папок
        Синтаксис: sync <drive_path> <local_path> <sync_mode>

        Args:
            drive_path (str): Путь к папке в Google Drive.
            local_path (str): Локальный путь для синхронизации.
            sync_mode (int): Режим синхронизации (download - из облака в локального репозиторий, upload - из локального репозитория в облако).
        """
        stop_loading = UserInterface.show_loading_message()

        if sync_mode == "download":
            FileManager.sync_from_cloud(drive_path, local_path)
        else:
            FileManager.sync_to_cloud(local_path, drive_path)

        stop_loading()
        UserInterface.show_success("Synchronization completed successfully")

    @staticmethod
    def sync_from_cloud(drive_path, local_path):
        """
        Синхронизация из облака в локальный репозиторий.
        """
        # Проверка существования локальной директории
        if not os.path.exists(local_path):
            os.makedirs(local_path)

        # Получение идентификатора папки на Google Drive
        folder_id = PathNavigator.validate_path(drive_path, current_path=os.getenv("GOOGLE_CLOUD_CURRENT_PATH"))
        if not folder_id:
            UserInterface.show_error("Drive path is incorrect")
            return

        # Рекурсивное скачивание содержимого папки
        FileManager._download_folder_contents(drive_path, local_path)

    @staticmethod
    def sync_to_cloud(local_path, drive_path):
        """
        Синхронизация из локального репозитория в облако.
        """
        # Проверка существования локальной директории
        if not os.path.exists(local_path):
            UserInterface.show_error("Local path does not exist")
            return

        # Получение идентификатора папки на Google Drive
        folder_id = PathNavigator.validate_path(drive_path, current_path=os.getenv("GOOGLE_CLOUD_CURRENT_PATH"),
                                                check_file=False)
        if not folder_id:
            UserInterface.show_error("Drive path not found, i create this path")
            FileManager.mkdir(drive_path, True)

        # Рекурсивное загрузка содержимого локальной папки
        FileManager._upload_folder_contents(local_path, drive_path)

    @staticmethod
    def _download_folder_contents(drive_path, local_path):
        folder_id = PathNavigator.validate_path(drive_path, current_path=os.getenv("GOOGLE_CLOUD_CURRENT_PATH"))
        needed_copy = PathNavigator.gather_structure(folder_id)

        iterator = iter(needed_copy)

        # использую стандартный итератор для фикса проблемы с извлечением следующего элемента при "?"
        for file in iterator:

            if file == "!":
                next_file = next(iterator, None)
                if not next_file:
                    break
                elif next_file == "?":
                    file = "?"
                else:
                    local_path = os.path.join(local_path, next_file['name'])
                    # Проверка существования локальной директории
                    if not os.path.exists(local_path):
                        UserInterface.show_message(f"Create path {local_path}")
                        os.mkdir(local_path)
                    continue

            if file == "?":
                local_path = os.path.dirname(local_path)

            if file != '!' and file != '?':
                path = PathNavigator.pwd(file['id'])
                path = path.replace("MyDrive", "~", 1)
                UserInterface.show_message(f"Download file {path}")
                file_local_path = os.path.join(local_path, file['name'])
                FileManager.export(path, file_local_path)

    @staticmethod
    def _upload_folder_contents(local_path, drive_path):
        drive_path.strip("/")
        for item in os.listdir(local_path):
            item_local_path = os.path.join(local_path, item)

            if os.path.isdir(item_local_path):
                # Обработка директорий на первом уровне
                dir_drive_path = os.path.join(drive_path, item)
                FileManager.mkdir(dir_drive_path, True)
                # Загружаем содержимое директории на первом уровне
                FileManager._upload_folder_contents(item_local_path, dir_drive_path)
            else:
                # Обработка файлов на первом уровне
                UserInterface.show_message(f"Upload file: {item_local_path}")
                FileManager.upload(drive_path, item_local_path, item, uploadType="MultipartUpload")

    @staticmethod
    def _confirm_upload():
        """
        Запрашивает подтверждение действия у пользователя.

        Args:
            name_file (str): Имя файла, над которым будет производиться действие.
        """
        while True:
            response = input("Should I continue sending the file (Y/N): ").strip().lower()
            if response in ('yes', 'y'):
                return True
            elif response in ('no', 'n'):
                return False
            else:
                UserInterface.show_message(
                    [{"text": f"Please enter 'yes' or 'no' to confirm. ", "color": "bright_yellow"}]
                )

    @staticmethod
    def upload(path, local_path="./", name=None, mimeType=None, uploadType="SimpleUpload"):
        """
        Загружаем файл с локального компьютера на Google Drive.

        Args:
            path (str): Путь в Google Drive, куда будет загружен файл.
            local_path (str): Локальный путь к файлу для загрузки.
            name (str): Опционально. Указывает имя для загружаемого файла.
            mimeType (str): Опционально. Указывает MIME-тип загружаемого файла.
            uploadType (str): Опционально. Указывает тип метода загрузки:
                - SimpleUpload: Базовый метод загрузки для небольших файлов (5 МБ или меньше).
                - MultipartUpload: Метод загрузки для небольших файлов (5 МБ или меньше).
                - ResumableUpload: Метод многократной загрузки для крупных файлов с возможностью повтора (более 5 МБ).
        """
        stop_loading = UserInterface.show_loading_message()

        TypesUpload = {
            "SimpleUpload": FileManager.SimpleUpload,
            "MultipartUpload": FileManager.MultipartUpload,
            "ResumableUpload": FileManager.ResumableUpload
        }

        if os.path.isfile(local_path):
            file_size = os.path.getsize(local_path)
            if uploadType != 'ResumableUpload' and file_size >= 6 * 1024 * 1024:  # 6 MB
                stop_loading()
                UserInterface.show_message(
                    [{"text": f"File '{local_path}' exceeds the size limit of 6 MB, it is better to use ResumableUpload.",
                      "color": "bright_yellow"}]
                )
                if FileManager._confirm_upload():
                    stop_loading = UserInterface.show_loading_message()
                    TypesUpload[uploadType](path, local_path, name, mimeType)
                    stop_loading()
                    return
                else:
                    UserInterface.show_message("The upload has been canceled. ")
                    return
            if uploadType == 'SimpleUpload' and (name or mimeType):
                stop_loading()
                UserInterface.show_message(
                    [{
                         "text": f"When you used a simple download, you can't specify the file name and type. I recommend u should use ResumableUpload",
                         "color": "bright_yellow"}]
                )
                if FileManager._confirm_upload():
                    stop_loading = UserInterface.show_loading_message()
                    TypesUpload[uploadType](path, local_path, name, mimeType)
                    stop_loading()
                    return
                else:
                    UserInterface.show_message("The upload has been canceled. ")
                    return
            TypesUpload[uploadType](path, local_path, name, mimeType)
        else:
            UserInterface.show_error(f"File '{local_path}' does not exist.")
        stop_loading()
        return

    @staticmethod
    def creating_metadata_file(parents_id, name_file, mimeType):
        """
        Создаем метаданные файла перед записыванием туда даннных
        """
        # Метод для создания файла в Google Cloud
        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/json'
        }

        url = f'https://www.googleapis.com/drive/v3/files'

        body = {
            "name": name_file,
            'parents': [parents_id] if parents_id else [],
            'fields': 'id'
        }

        if mimeType:
            body["mimeType"] = mimeType

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            UserInterface.show_success("Creating file metadata complete!")
            return response.json()
        else:
            UserInterface.show_error(f'Failed then create metadata file. Status code: {response.status_code}')
            return None

    @staticmethod
    def SimpleUpload(path, local_path="./", name=None, mimeType=None):
        """
        Используйте этот тип загрузки для передачи небольшого медиафайла
        (5 МБ или меньше) без предоставления метаданных/ Но я все равно их задаю,
        Так как потом будут траблы с преобразованием полученной много весящей пустышки
        """
        # Дополнительные проверки на существоания файла!!!
        try:
            with open(local_path, "rb") as file:
                file_bytes = file.read()
        except FileNotFoundError:
            UserInterface.show_error(f"File {local_path} not found")
            return None
        except IsADirectoryError:
            UserInterface.show_error(f"Path {local_path} is a directory, not a file")
            return None

        file_id = FileManager.creating_metadata_file(os.getenv("GOOGLE_CLOUD_CURRENT_PATH"),
                                           os.path.basename(local_path),
                                           None)['id']

        if not file_id:
            return

        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/octet-stream'
        }

        url_upload = f'https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media'

        response_upload = requests.patch(url_upload, headers=headers, data=file_bytes)

        if response_upload.status_code == 200:
            UserInterface.show_success("Uploading file complete!")
            return response_upload.json()
        else:
            UserInterface.show_error(f'Failed to upload file. Status code: {response_upload.status_code}')
            return None

    @staticmethod
    def MultipartUpload(path, local_path, name=None, mimeType=None):
        """
        «Используйте этот тип загрузки для передачи небольшого файла
        (5 МБ или меньше) вместе с метаданными, описывающими файл, в одном запросе.
        """
        parents_id = PathNavigator.validate_path(path, os.getenv("GOOGLE_CLOUD_CURRENT_PATH"), check_file=True)
        # Дополнительные проверки на существоания файла!!!
        try:
            with open(local_path, "rb") as file:
                file_bytes = file.read()
        except FileNotFoundError:
            UserInterface.show_error(f"File {local_path} not found")
            return None
        except IsADirectoryError:
            UserInterface.show_error(f"Path {local_path} is a directory, not a file")
            return None

        file_id = FileManager.creating_metadata_file(parents_id,
                                                     name if name else os.path.basename(local_path),
                                                     mimeType)['id']

        if not file_id:
            return

        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': "application/json"
        }
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"

        url_upload = f'https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=multipart'

        response_upload = requests.patch(url_upload, headers=headers, data=file_bytes)

        if response_upload.status_code == 200:
            UserInterface.show_success("Uploading file complete!")
            return response_upload.json()
        else:
            UserInterface.show_error(f'Failed to upload file. Status code: {response_upload.status_code}')
            return None

    @staticmethod
    def _determine_chunk_size(file_size):
        """
        Подбираем размер чанка в зависимости от размера файла
        """
        if file_size <= 50 * 1024 * 1024:  # ≤ 50 MB
            return 1 * 1024 * 1024  # 1 MB
        elif file_size <= 200 * 1024 * 1024:  # > 50 MB and ≤ 200 MB
            return 5 * 1024 * 1024  # 5 MB
        elif file_size <= 1 * 1024 * 1024 * 1024:  # > 200 MB and ≤ 1 GB
            return 10 * 1024 * 1024  # 10 MB
        else:  # > 1 GB
            return 20 * 1024 * 1024  # 20 MB

    @staticmethod
    def ResumableUpload(path, local_path, name=None, mimeType=None):
        """
        используйте этот тип загрузки для больших файлов (более 5 МБ)
        и при высокой вероятности прерывания сети
        """
        stop_loading = UserInterface.show_loading_message()

        parents_id = PathNavigator.validate_path(path,
                                                 os.getenv("GOOGLE_CLOUD_CURRENT_PATH"),
                                                 check_file=True)

        # Создаем метаданные файла
        metadata = {
            'name': name if name else os.path.basename(local_path),
            'parents': [parents_id],
            'fields': 'id'
        }
        if mimeType:
            metadata['mimeType'] = mimeType

        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Upload-Content-Type': mimeType if mimeType else 'application/octet-stream',
        }

        url_resumable_upload = f'https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable'

        #  Действуем строго согласно документации: https://developers.google.com/drive/api/guides/manage-uploads
        # Отправляем первоначальный запрос и получаем URI возобновляемого сеанса.
        start_response = requests.post(url_resumable_upload, headers=headers, json=metadata)
        if start_response.status_code != 200:
            UserInterface.show_error(f'Failed to start resumable upload. Status code: {start_response.status_code}: {start_response.text}')
            return None

        # Если все ок, извлекаем Location из заголовков
        location = start_response.headers.get('Location')

        if not location:
            UserInterface.show_error(
                f'No Location header in response. Status code: {start_response.status_code}: {start_response.text}')
            return None

        try:
            file_size = os.path.getsize(local_path)
            with open(local_path, "rb") as file:
                file_bytes = file.read()
        except FileNotFoundError:
            UserInterface.show_error(f"File {local_path} not found")
            return None
        except IsADirectoryError:
            UserInterface.show_error(
                f"Path {local_path} is a directory, not a file"
            )
            return None

        # Проверяем, сколько данных уже было загружено
        if f'BYTES_UPLOADED_{name}' in os.environ:
            bytes_uploaded = int(os.environ['BYTES_UPLOADED'])
        else:
            os.environ[f'BYTES_UPLOADED_{name}'] = '0'
            bytes_uploaded = 0

        # Загрузаем данные и отслеживаем состояние загрузки.
        chunk_size = FileManager._determine_chunk_size(file_size)
        uploading_update, stop_uploading = UserInterface.show_upload_process_message()
        stop_loading()
        with open(local_path, "rb") as file:
            while bytes_uploaded < file_size:
                chunk = file.read(chunk_size)
                start_byte = bytes_uploaded
                os.environ[f'BYTES_UPLOADED_{name}'] = str(start_byte)
                end_byte = min(bytes_uploaded + chunk_size - 1, file_size - 1)

                headers['Content-Range'] = f'bytes {start_byte}-{end_byte}/{file_size}'

                upload_response = requests.put(location, headers=headers, data=chunk)

                if upload_response.status_code not in [200, 201, 308]:
                    UserInterface.show_error(
                        f'Failed to upload chunk. Status code: {upload_response.status_code}: {upload_response.text}')
                    stop_uploading()
                    return None

                bytes_uploaded += len(chunk)
                uploading_update((bytes_uploaded / file_size) * 100)
        stop_uploading()
        UserInterface.show_success("Resumable uploading file complete!")
        return upload_response.json()

    @staticmethod
    def ChangeMime(path, new_mimeType):
        """
        change-mime: Изменение MIME-типа файла в Google Drive.
        Синтаксис: change-mime <drive_path> <new_mimeType>

        Args:
            path (str): Путь к файлу в Google Drive.
            new_mimeType (str): Новый MIME-тип, который нужно установить.
        """
        stop_loading = UserInterface.show_loading_message()

        file_id = PathNavigator.validate_path(path, os.getenv("GOOGLE_CLOUD_CURRENT_PATH"), check_file=True)

        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/json'
        }

        url = f'https://www.googleapis.com/drive/v3/files/{file_id}'
        body = {
            'mimeType': new_mimeType
        }

        response = requests.patch(url, headers=headers, json=body)

        if response.status_code == 200:
            UserInterface.show_success(f"MIME-type changed successfully for file {path}.")
        else:
            UserInterface.show_error(
                f"Failed to change MIME-type. Status code: {response.status_code}: {response.text}")

        stop_loading()

    @staticmethod
    def _confirm_export(mimeType):
        """
        Запрашивает подтверждение действия у пользователя.

        Args:
            name_file (str): Имя файла, над которым будет производиться действие.
        """
        UserInterface.show_message(
            [{"text": f"before downloading this file, you need to convert it, select the type to convert: {mimeType}",
              "color": "bright_yellow"}]
        )
        UserInterface.show_message(
            [{
                 "text": f"If you don't want to send file now enter no. ",
                 "color": "bright_yellow"}]
        )

        while True:
            UserInterface.show_message([{
                    "text": f"Your choice: ",
                    "color": "bright_yellow"}],
                    end="")
            response = input().strip().lower()
            if response in mimeType:
                return response
            elif response in ('no', 'n'):
                return None
            else:
                UserInterface.show_message(
                    [{"text": f"Please enter correct mimeTypes or 'no' to confirm. ", "color": "bright_yellow"}]
                )

    @staticmethod
    def export(path, local_path="", mimeType=None):
        """
        Экспорт файла из Google Drive в указанный формат и загрузка на локальный компьютер.
        Синтаксис: export <drive_path> <mimeType> <local_path>

        Args:
            path (str): Путь к файлу в Google Drive.
            mimeType (str): MIME-тип, в который нужно экспортировать файл.
            local_path (str): Путь на локальном компьютере для сохранения экспортированного файла.
        """
        stop_loading = UserInterface.show_loading_message()

        file_id = PathNavigator.validate_path(path, os.getenv("GOOGLE_CLOUD_CURRENT_PATH"), check_file=True)
        file_metadata = FileManager.get_file_metadata(file_id)
        source_mimeType = file_metadata['mimeType']

        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/json'
        }

        valid_mimeType = FileManager.export_formats(mimeType=source_mimeType, called_directly=False)

        if valid_mimeType is None:
            UserInterface.show_error("No export formats available for this file type.")
            stop_loading()
            return

        # Если mimeType не требует конвертации и указанный пользователем совпадает с исходным или не указан
        if valid_mimeType == 'NotRequire' and (not mimeType or mimeType == source_mimeType):
            url = f'https://www.googleapis.com/drive/v3/files/{file_id}?alt=media'
            response = requests.get(url, headers=headers, stream=True)
        else:
            # Если mimeType указан и требует конвертации
            if mimeType:
                if mimeType in valid_mimeType:
                    url = f'https://www.googleapis.com/drive/v3/files/{file_id}/export'
                    params = {'mimeType': mimeType}
                    response = requests.get(url, headers=headers, params=params, stream=True)
                else:
                    UserInterface.show_error("Invalid MIME type for export.")
                    stop_loading()
                    return
            else:
                # Запрос пользователю указать mimeType
                if mimeType is None:
                    mimeType = FileManager.export_formats(path=path, called_directly=False)
                else:
                    mimeType = FileManager.export_formats(mimeType=mimeType, called_directly=False)

                if mimeType is None:
                    UserInterface.show_error("No export formats available for this file type.")
                    stop_loading()
                    return
                stop_loading()
                mimeType = FileManager._confirm_export(mimeType)
                stop_loading = UserInterface.show_loading_message()
                if not mimeType:
                    stop_loading()
                    return

                url = f'https://www.googleapis.com/drive/v3/files/{file_id}/export'
                params = {'mimeType': mimeType}
                response = requests.get(url, headers=headers, params=params, stream=True)

        if response.status_code == 200:
            local_path = os.path.join(os.getcwd(), local_path)
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            UserInterface.show_success(f"File exported and downloaded successfully to {local_path}.")
        else:
            UserInterface.show_error(f"Failed to export file. Status code: {response.status_code}: {response.text}")
        stop_loading()

    @staticmethod
    def export_formats(path=None, mimeType=None, called_directly=True):
        """
        Получает список поддерживаемых форматов экспорта для заданного MIME-типа файла в Google Drive.
        Можно указать либо MIME-тип, либо напрямую указать файл, который надо экспортировать.

        Аргументы:
            mimeType (str): MIME-тип файла, для которого требуется получить список поддерживаемых форматов экспорта.
            path (str): Путь к файлу в Google Drive. Если указан, будет использован MIME-тип этого файла.
            called_directly (bool): Флаг, указывающий, был ли метод вызван напрямую пользователем.
        """

        # MIME-типы, которые можно скачать напрямую
        downloadable_mime_types = [
            'application/zip',  # Zip file
            'application/pdf',  # PDF file
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # Microsoft Word (docx)
            'application/msword',  # Microsoft Word (doc)
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # Microsoft Excel (xlsx)
            'application/vnd.ms-excel',  # Microsoft Excel (xls)
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # Microsoft PowerPoint (pptx)
            'application/vnd.ms-powerpoint',  # Microsoft PowerPoint (ppt)
            'image/jpeg',  # JPEG image
            'image/png',  # PNG image
            'image/gif',  # GIF image
            'image/tiff',  # TIFF image
            'image/bmp',  # BMP image
            'text/plain',  # Plain text file
            'text/csv',  # CSV file
            'text/html',  # HTML file
            'text/xml',  # XML file
            'application/json',  # JSON file
            'video/mp4',  # MP4 video file
            'video/x-msvideo',  # AVI video file
            'video/quicktime',  # QuickTime video file
            'audio/mpeg',  # MP3 audio file
            'audio/wav',  # WAV audio file
            'audio/x-aiff',  # AIFF audio file
        ]

        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/json'
        }

        # Если указан путь, получаем MIME-тип файла
        if path:
            file_id = PathNavigator.validate_path(path, os.getenv("GOOGLE_CLOUD_CURRENT_PATH"), check_file=True)
            file = FileManager.get_file_metadata(file_id)
            mimeType = file['mimeType']

        url = 'https://www.googleapis.com/drive/v3/about'
        params = {'fields': 'exportFormats'}

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            UserInterface.show_error(
                f"Failed to retrieve export formats. Status code: {response.status_code}: {response.text}")
            return

        export_formats = response.json().get('exportFormats', {})

        if mimeType in downloadable_mime_types:
            if called_directly:
                UserInterface.show_success("This format does not require conversion to download.")
            return "NotRequire"

        if mimeType not in export_formats:
            if called_directly:
                UserInterface.show_error("This format is not available for download.")
            return None

        if called_directly:
            for export_type in export_formats[mimeType]:
                UserInterface.show_message(export_type)
        else:
            return export_formats[mimeType]
