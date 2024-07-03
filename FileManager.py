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
    def get_by_mimeType(key):
        try:
            return BiDict.forward[key]
        except KeyError:
            UserInterface.show_message(
                [
                    {"text": "This mimeType is not extension", "color": "red"},
                    {"text": "Extensions mimeType: ", "color": "bright_yellow", "clear": "\n"}
                ]
            )
            PathNavigator.get_mime_description()

    @staticmethod
    def get_by_extension(value):
        try:
            return BiDict.backward.get(value)
        except KeyError:
            UserInterface.show_message(
                [
                    {"text": "This extension is not extension", "color": "red"},
                    {"text": "Extensions extension: ", "color": "bright_yellow", "clear": "\n"}
                ]
            )
            PathNavigator.get_mime_description()

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
            'fields': 'name, id, parents, mimeType'
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
    def ls(path, show_long=False):
        """
        Отображает список файлов в указанной директории.

        Args:
            path (str): Путь к директории для отображения. Если None, используется текущая директория.
            show_long (bool): Если True, используется длинный формат отображения (выводит имя файла, его идентификатор и тип).
        """
        stop_loading = UserInterface.show_loading_message()

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
                        UserInterface.show_message(f"{file['name']} {file['id']} {file['mimeType']} {FileManager.format_size(int(file['size']))}. ")
                    else:
                        UserInterface.show_message(f"{file['name']} {file['id']} {file['mimeType']} N/A. ")
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
        if create_parents:
            gather_needed = PathNavigator.gather_needed_paths(path)
            start_path, paths_to_create = gather_needed.values()
            new_paths_id = []

            while paths_to_create:
                start_path = FileManager.mkdir(paths_to_create[0], start_path=start_path)

                new_paths_id.append(start_path)
                paths_to_create.pop(0)

            return new_paths_id
        # проигрываем анимацию загрузки
        stop_loading = UserInterface.show_loading_message()

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
            parents_id = PathNavigator.validate_path(path)

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
    def cp(source: str, destination: str, recursive=False):
        """
        Копирует директории или файлы source в destination.

        Args:
            source (str): Путь к тому, что надо скопировать.
            destination (str): Путь куда надо скопировать.
            recursive (bool): Нужно ли копировать рекурсивно.
        """
        stop_loading = UserInterface.show_loading_message()

        source_id = PathNavigator.validate_path(source, os.getenv("GOOGLE_CLOUD_CURRENT_PATH"), check_file=True)
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

            elif file == "?":
                previous_file = FileManager.get_file_metadata(destination_id)
                destination_id = previous_file['parents'][0]

            else:
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
            UserInterface.show_message(
                [{"text": f"Are you sure you want to delete this file: ", "color": "bright_yellow"}]
            )
            response = input().strip().lower()
            if response in ('yes', 'y'):
                return True
            elif response in ('no', 'n'):
                return False
            else:
                UserInterface.show_message(
                    [{"text": f"Please enter 'yes' or 'no' to confirm. ", "color": "bright_yellow"}]
                )

    @staticmethod
    def rm(path, recursive, verbose, interactive):
        """
        Удаляет директорию или файл, путь к которму path.

        Args:
            path (str): Путь к тому, что надо удалить.
            verbose (bool): Выводить ли дополнительную информацию, о этапах удаления файла.
            interactive (bool): Запрашивать согласие перед каждым удалением файла, в случае отказа, файл не будет удлён.
            recursive (bool): Каскадное удаление файлов в path.
        """
        stop_loading = UserInterface.show_loading_message()

        id_remove = PathNavigator.validate_path(path, os.getenv("GOOGLE_CLOUD_CURRENT_PATH"), check_file=True)
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
                    if FileManager._confirm_action(file_remove_root['name']):
                        UserInterface.show_message("The action is confirmed. We continue the execution. ")
                        response = FileManager._remove_file(id_remove)
                    else:
                        UserInterface.show_message("The action has been canceled. ")
                        stop_loading()
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
                    if FileManager._confirm_action(file_remove_root['name']):
                        UserInterface.show_message("The action is confirmed. We continue the execution. ")
                        response = FileManager._remove_file(id_remove)
                    else:
                        UserInterface.show_message("The action has been canceled. ")
                        stop_loading()
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
                if FileManager._confirm_action(file_remove_root['name']):
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
    def mv(source_path: str, destination_path: str):
        """
        НЕ РАБОТАЕТ ИЗ ЗА ПРИКОЛОВ GoogleDriveApi, исключение не вызывает.
        Перемещает source_path в destination_path.

        Args:
            source_path (str): Путь к тому, что надо переместить.
            destination_path (str): Путь куда ндо переместить.
        """
        source_id = PathNavigator.validate_path(source_path, current_path=os.getenv("GOOGLE_CLOUD_CURRENT_PATH"), check_file=True)
        destination_id = PathNavigator.validate_path(destination_path, current_path=os.getenv("GOOGLE_CLOUD_CURRENT_PATH"))

        if not source_id:
            UserInterface.show_error("Source path is incorrect")
            return

        if not destination_id:
            UserInterface.show_error("Destination path is incorrect")
            return

        source_metadata = FileManager.get_file_metadata(source_id)

        # Метод для обновления временных меток файла в Google Drive
        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
            'Content-Type': 'application/json'
        }

        url = f'https://www.googleapis.com/drive/v3/files/{source_id}'

        body = {
            'removeParents': source_metadata.get("parents"),
            'addParents': destination_id,
            'fields': 'id, parents'  # Указываем поля, которые хотим получить в ответе
        }

        response = requests.patch(url, headers=headers, json=body)

        if response.status_code == 200:
            UserInterface.show_message(f"Transfer is completed, new parents id: {response.json()['id']}")
            return response.json()
        else:
            UserInterface.show_error(f'Failed to move file times. Status code: {response.status_code}: {response.text}')
            return None

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
    def info():
        pass

    @staticmethod
    def mimeType():
        """
        Функция для вывода списка mimeType и их расширений.
        """
        for mime in PathNavigator.get_mime_description():
            UserInterface.show_message(f"{mime['mime']} ({mime['extension']}): {mime['description']}")

    @staticmethod
    def trash(path):
        """
        Перемещает файл по пути path в корзину

        Args:
            path (str): путь к тому что надо переместить в корзину.
        """
        stop_loading = UserInterface.show_loading_message()

        file_id = PathNavigator.validate_path(
            path,
            os.getenv("GOOGLE_CLOUD_CURRENT_PATH"),
            check_file=True
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
    def restore(path):
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
            check_file=True
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
        # URL запроса
        url = 'https://www.googleapis.com/drive/v3/files/trash'

        # Заголовки
        headers = {
            'Authorization': f'Bearer {FileManager._creds().token}',
        }

        # Отправка запроса
        response = requests.delete(url, headers=headers)

        if response.status_code == 204:
            print('Trash emptied successfully.')
        else:
            print(f'Failed to empty trash: {response.text}')

