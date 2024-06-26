import os
import sys
from typing import Any
import argparse
import re
import mimetypes

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
import requests
from requests import Response

SCOPES = ['https://www.googleapis.com/auth/drive']


class ResponseTeg:
    def __init__(self, text, status_code):
        self.text_response = text
        self.status_code_response = status_code

    @property
    def text(self):
        return self.text_response

    @property
    def status_code(self):
        return self.status_code_response


class GoogleCloudTerminal:
    # Статическая переменная для хранения учетных данных
    creds = None
    # Статическая переменная для хранения идентификатора корня
    MyDriveID = "root"
    # положение пользователя
    current_path = MyDriveID

    def __init__(self, token_path="token.json", credentials_path="credentials.json"):
        """
        Инициализирует GoogleCloudTerminal, устанавливает текущий путь и запускает авторизацию.

        Args:
            token_path (str): Путь к файлу токена.
            credentials_path (str): Путь к файлу учетных данных.
        """
        # Чтобы это работало и на винде, подходи м к файлам по абсолютному пути
        self.token_path = os.path.join(os.path.dirname(__file__), "./token.json")
        self.credentials_path = os.path.join(os.path.dirname(__file__), "./credentials.json")

        #авто запуск авторизации
        self._autorization()
        #получаем идентификатор драйвера пользователя
        GoogleCloudTerminal.MyDriveID = FileManager.get_user_drive_id()
        GoogleCloudTerminal.current_path = FileManager.get_user_drive_id()

    def _autorization(self):
        """
            Функция для регистрации Google Drive API v3.
            Если пользователь не дал разрешения моему ПО, то кидает на регистрацю
        """
        # Файл token.json хранит учетные данные пользователя и обновляет его автоматически, через запрос (Request)
        if os.path.exists(self.token_path):
            # статический метод класса, который создает экземпляр учетных данных из файла json
            GoogleCloudTerminal.creds = Credentials.from_authorized_user_file(self.token_path)
        # Если нет действительных учетных данных, авторизуйте пользователя.
        if not GoogleCloudTerminal.creds or not GoogleCloudTerminal.creds.valid:
            if GoogleCloudTerminal.creds and GoogleCloudTerminal.creds.expired and GoogleCloudTerminal.creds.refresh_token:
                try:
                    # если creds != None и учетные данные просрочились, просто обновляем их запросом
                    GoogleCloudTerminal.creds.refresh(Request())
                except RefreshError:
                    # Если не удалось обновить токен, удаляем token.json и повторяем авторизацию
                    os.remove(self.token_path)
                    GoogleCloudTerminal.creds = None

            if not GoogleCloudTerminal.creds:
                # создаем поток авторизации, то бишь получаем от имени моего ПО данные для авторизации в диске юзера
                # собственно данные проекта, приложение, меня как разработчика лежат в credentials
                # потом сразу пускаем на выбранном ОС порте (порт=0) сервер для прослушивания ответа от потока авторизации
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, scopes=SCOPES)
                GoogleCloudTerminal.creds = flow.run_local_server(port=0)
                # Сохраните учетные данные для следующего запуска.
                with open(self.token_path, 'w') as token:
                    token.write(GoogleCloudTerminal.creds.to_json())

    def execute_command(self, input_string: str):
        """
        Выполняет команду, введенную пользователем.

        Эта функция принимает строку команды, разбирает её на команду и аргументы,
        а затем вызывает соответствующий метод для выполнения этой команды.

        Args:
            input_string (str): Строка команды, введенная пользователем.
        """
        command, args = CommandParser.parser_command(input_string)

        if command == 'cd':
            return self.change_directory(args)
        elif command == 'ls':
            return self.list_files(args)
        elif command == 'mkdir':
            return self.make_directory(args)
        elif command == 'cp':
            return self.copy(args)
        elif command == 'rm':
            return self.remove(args)
        else:
            print(f"Unknown command: {command}")
        """
        try:
            command, args = CommandParser.parser_command(input_string)

            if command == 'cd':
                self.change_directory(args)
            elif command == 'ls':
                self.list_files(args)
            elif command == 'mkdir':
                self.make_directory(args)
            elif command == 'cp':
                self.copy(args)
            else:
                print(f"Unknown command: {command}")

        except Exception:
            print(f"Unknown command")"""

    def change_directory(self, args):
        """
        Изменяет текущий рабочий каталог на указанный путь, если он существует.

        Args:
            path_new (str): Новый путь для перехода.
        """
        try:
            new_path = PathNavigator.validate_path(path=args.path, current_path=GoogleCloudTerminal.current_path)

            if new_path:
                GoogleCloudTerminal.current_path = new_path
                return new_path
        except Exception:
            print("Error: New path is incorrect")

    def list_files(self, args):
        """
        Метод для вывода списка файлов в текущем каталоге.
        Args:
            args: Аргументы для команды 'ls'.
        """
        try:
            return FileManager.ls(path=args.path, show_long=args.long)

        except Exception:
            print("Error: ls called except")

    def make_directory(self, args):
        """
        Метод для создания директории
        Args:
            args: Аргументы для команды 'mkdir'.
        """
        try:
            return FileManager.mkdir(path=args.path[0], create_parents=args.parents)
        except Exception:
            print("Error: ls called except")

    def copy(self, args):
        """
        Метод для копирования файлов/директорий
        Args:
            args: Аргументы для команды 'cp'.
        """
        try:
            FileManager.cp(source=args.source, destination=args.destination, recursive=args.recursive)
        except Exception:
            print("Error: ls called except")

    def remove(self, args):
        """
        Метод для удаления файлов/директорий
        Args:
            args: Аргументы для команды 'rm'.
        """
        FileManager.rm(path=args.path, recursive=args.recursive, verbose=args.verbose, interactive=args.interactive)


class FileManager:

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
            'Authorization': f'Bearer {GoogleCloudTerminal.creds.token}',
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
            print(f"Error while retrieving user drive ID: {e}")
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
            'Authorization': f'Bearer {GoogleCloudTerminal.creds.token}'
        }

        # URL запроса для получения списка файлов Google Drive API v3
        url = 'https://www.googleapis.com/drive/v3/files'

        # Параметры запроса
        params = {
            "corpora": "user",
            'fields': 'files(name, id, mimeType, parents)',
        }

        # Отправляем GET-запрос к API Google Drive
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Вызываем исключение в случае ошибки HTTP

            files = response.json().get('files', [])

            if called_directly:
                if not files:
                    print('Your google drive is empty')
                else:
                    print('Files:')
                    for file in files:
                        print(f'{file["name"]}:{file["id"]}')

            return files

        except requests.exceptions.RequestException as e:
            print(f'Failed to retrieve files: {e}')
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
            'Authorization': f'Bearer {GoogleCloudTerminal.creds.token}',
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
            # print(f'Failed to get file metadata. Status code: {response.status_code}')
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
            else:
                print(f'File with ID "{file_id}" not found.')
                return None

        if name:
            file_id = FileManager.find_file_by_name(files, name, mime_type)
            if file_id:
                return file_id
            else:
                print(f'File with name "{name}" not found.')
                return None

    @staticmethod
    def ls(path, show_long=False):
        """
        Отображает список файлов в указанной директории.

        Args:
            path (str): Путь к директории для отображения. Если None, используется текущая директория.
            show_long (bool): Если True, используется длинный формат отображения (выводит имя файла, его идентификатор и тип).
        """

        files = FileManager.get_list_of_files(called_directly=False)

        if path:
            path_parts_id = PathNavigator.validate_path(path=path, current_path=GoogleCloudTerminal.current_path)
        else:
            path_parts_id = GoogleCloudTerminal.current_path

        if not path_parts_id:
            print("Path is incorrect. ")
            return

        for file in files:
            if 'parents' in file.keys() and file['parents'][0] == path_parts_id:
                if show_long:
                    print(file['name'], " ", file['id'], " ", file['mimeType'])
                else:
                    print(file['name'])

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

        path_parts = re.sub('\n', "", path)

        path_parts = path_parts.strip("/").split("/")
        name_path = path_parts[-1]

        if start_path:
            parents_id = start_path
        else:
            path_parts = "/".join(path_parts[:-1])

            parents_id = PathNavigator.validate_path(path_parts, GoogleCloudTerminal.current_path)

            if not parents_id:
                print("Path is incorrect")
                return None

        if called_directly:
            print("Create path: ", path, name_path, parents_id)

        # Создаем заголовок с авторизационным токеном
        headers = {
            'Authorization': f'Bearer {GoogleCloudTerminal.creds.token}',
            'Content-Type': 'application/json',
        }

        # URL запроса для получения списка файлов Google Drive API v3
        url = 'https://www.googleapis.com/drive/v3/files'

        # Проверяем есть ли в destination_id папки с таким же именем
        lst = [child['name'] for child in PathNavigator.get_child_files(parents_id)]
        count_names = lst.count(name_path)

        if count_names:
            name_path = f"{name_path}_{count_names}"

        body = {
            "name": name_path,
            "mimeType": "application/vnd.google-apps.folder",
            'parents': [parents_id]
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            if called_directly:
                print('Create folber compleate')
            return response.json()['id']
        else:
            if called_directly:
                print(f'error when creating folber: {response.status_code} - {response.text}')
            return None

    @staticmethod
    def touch(path):
        # Метод для создания файла в Google Cloud
        pass

    @staticmethod
    def cp(source: str, destination: str, recursive=False):
        source_id = PathNavigator.validate_path(source, GoogleCloudTerminal.current_path, check_file=True)
        destination_id = PathNavigator.validate_path(destination, GoogleCloudTerminal.current_path)
        # проверяем корректность обоих путей
        if not source_id:
            print("Source is incorrect")
            return None
        if not destination_id:
            print("Destination is incorrect")
            return None

        # сначала проверим тип файла, и если он не папка, то независимо от recursive
        # копируем только этот файл
        file_source = FileManager.get_file_metadata(source_id)

        if file_source['mimeType'] == 'application/vnd.google-apps.folder' and not recursive:
            if FileManager._copy_folder(file_source, destination_id):
                print(f'Folder copied successfully to {destination}')
        elif file_source['mimeType'] != 'application/vnd.google-apps.folder' and recursive:
            # так как у не папки детей быть не может, а лишняя предосторожность не помешает
            if FileManager._copy_file(file_source, destination_id):
                print(f'File copied successfully to {destination}')
        else:
            if FileManager._copy_directory(file_source, destination_id):
                print(f'Recursive files copied successfully to {destination}')

    @staticmethod
    def _copy_folder(source, destination_id):
        # Создаем папку, так как нельз их копировать...
        headers = {
            'Authorization': f'Bearer {GoogleCloudTerminal.creds.token}',
            'Content-Type': 'application/json',
        }

        # URL запроса для получения списка файлов Google Drive API v3
        url = 'https://www.googleapis.com/drive/v3/files'

        name_copy_folder = f"Copy of {source['name']}"

        # Проверяем есть ли в destination_id папки с таким же именем
        lst = [child['name'] for child in PathNavigator.get_child_files(destination_id)]
        count_names = lst.count(name_copy_folder)

        if count_names:
            name_copy_folder = f"{count_names+1} copy of {source['name']}"

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
        # Реализация копирования одного файла
        headers = {
            'Authorization': f'Bearer {GoogleCloudTerminal.creds.token}',
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
            print(f"Error copying file: {response.status_code} - {response.text}")
            return None

    @staticmethod
    def _copy_directory(source, destination_id):
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

            FileManager._copy_file(file, destination_id)

        return True

    @staticmethod
    def _remove_file(id_remove):

        if PathNavigator.get_child_files(id_remove):
            return ResponseTeg("Folder have child files", 403)

        headers = {
            'Authorization': f'Bearer {GoogleCloudTerminal.creds.token}'
        }

        # URL запроса для удаления файла Google Drive API v3
        url = f'https://www.googleapis.com/drive/v3/files/{id_remove}'

        response = requests.delete(url, headers=headers)

        return response

    @staticmethod
    def _recursive_remove_branch(verbose, interactive, remove_files_struct):

        remove_files_struct = iter(remove_files_struct[::-1])

        for file_remove in remove_files_struct:
            response = None

            if isinstance(file_remove, str):
                file_remove = next(remove_files_struct, None)

                if not file_remove:
                    break

            if verbose:
                print(f"I'll trying delete: {file_remove['name']} ({mimetypes.guess_extension(file_remove['mimeType'])}): {file_remove['id']}")

            if interactive:
                if FileManager._confirm_action(file_remove['name']):
                    print("The action is confirmed. We continue the execution. ")
                    response = FileManager._remove_file(file_remove['id'])
                else:
                    print("The action has been canceled. ")
                    continue
            else:
                response = FileManager._remove_file(file_remove['id'])

            if response.status_code == 204:
                print(f"{file_remove['name']} delete complete")
            else:
                print(f'error when deleting file: {response.status_code} - {response.text}')

    @staticmethod
    def _confirm_action(name_file):
        while True:
            response = input(f"Are you sure you want to delete this file: {name_file}? (yes/no): ").strip().lower()
            if response in ('yes', 'y'):
                return True
            elif response in ('no', 'n'):
                return False
            else:
                print("Please enter 'yes' or 'no' to confirm.")

    @staticmethod
    def rm(path, recursive, verbose, interactive):

        id_remove = PathNavigator.validate_path(path, GoogleCloudTerminal.current_path, check_file=True)
        file_remove_root = FileManager.get_file_metadata(id_remove)

        if not id_remove:
            return None

        # папку без рекурсиваного удаления, удалять нельзя
        if file_remove_root['mimeType'] == 'application/vnd.google-apps.folder':
            remove_files_struct = PathNavigator.gather_structure(id_remove)

            if not recursive and not remove_files_struct:
                response = None

                if interactive:
                    if FileManager._confirm_action(file_remove_root['name']):
                        print("The action is confirmed. We continue the execution. ")
                        response = FileManager._remove_file(id_remove)
                    else:
                        print("The action has been canceled. ")
                        return

                else:
                    if verbose:
                        print(f"I'll trying delete: {file_remove_root['name']} (folder): {file_remove_root['id']}")

                    response = FileManager._remove_file(id_remove)

                if response.status_code == 204:
                    print(f"{file_remove_root['name']} delete complete")
                else:
                    print(f'error when deleting file: {response.status_code} - {response.text}')

            elif recursive:
                response = None

                if verbose:
                    print(f"folder ({file_remove_root['name']}) have child files, i'll try to delete them.")
                    print(f"I'm starting to clean the branch")

                # чистим ветку
                FileManager._recursive_remove_branch(verbose, interactive, remove_files_struct)

                if verbose:
                    print(f"I'll trying delete: {file_remove_root['name']} (folder): {file_remove_root['id']}")

                if interactive:
                    if FileManager._confirm_action(file_remove_root['name']):
                        print("The action is confirmed. We continue the execution. ")
                        response = FileManager._remove_file(id_remove)
                    else:
                        print("The action has been canceled. ")
                        return
                else:
                    # удаляем корень очищенной ветки
                    response = FileManager._remove_file(id_remove)

                if response.status_code == 204:
                    print(f"{file_remove_root['name']} delete complete")
                    print(f'Recursive deletion is complete')
                else:
                    print(f'error when deleting file: {response.status_code} - {response.text}')
            else:
                print(f'error when deleting file: This folder have child files')

        else:
            response = None

            if interactive:
                if FileManager._confirm_action(file_remove_root['name']):
                    print("The action is confirmed. We continue the execution. ")
                    response = FileManager._remove_file(id_remove)
                else:
                    print("The action has been canceled. ")
                    return

            else:
                if verbose:
                    print(f"I'll trying delete: {file_remove_root['name']} (folder): {file_remove_root['id']}")

                response = FileManager._remove_file(id_remove)

            if response.status_code == 204:
                print(f"{file_remove_root['name']} delete complete")
            else:
                print(f'error when deleting file: {response.status_code} - {response.text}')


class PathNavigator:
    @staticmethod
    def validate_path(path: str, current_path=GoogleCloudTerminal.current_path, check_file=False):
        # ОПАСНО не указывать current_path напрямую, так как питон заполняет это поле,
        # базовым значением, которе мы указали в GCT.current_path = root
        """
        Проверяет и возвращает идентификатор каталога по указанному пути.

        Args:
            path (str): Путь для проверки.
            current_path (str): Текущий путь.

        Returns:
            str or None: Идентификатор папки, если путь существует, иначе None.
        """
        import re

        path = re.sub('\n',"", path)

        path_parts = path.strip("/").split("/")

        # ожидаемый конечный родитель
        if path_parts[0] == "~":
            should_parents = GoogleCloudTerminal.MyDriveID
            path_parts.pop(0)
            if not path_parts:
                return should_parents

        else:
            should_parents = current_path

        def check_parents(parents_id, path_index):
            """Рекурсивная функция для проверки каждого родителя до корневой папки"""
            post_path = FileManager.get_file_metadata(parents_id)

            # запрашиваем ид родителя
            post_path_id = post_path["parents"][0]

            if post_path_id == should_parents and len(path_parts) == path_index:
                return True

            name_post_path = FileManager.look_for_file(file_id=post_path_id)

            # если именя родителя этого пути не совпал с ожидаемым, выходим из рекурсии
            if name_post_path != path_parts[path_index]:
                return None

            return check_parents(post_path_id, path_index + 1)

        def handle_double_dots(current_path):
            """обработка .. в пути"""
            nonlocal should_parents
            if path_parts and path_parts[0] == "..":
                # получаем ид родителя и удаляем .. из пути
                should_parents = FileManager.get_file_metadata(current_path)['parents'][0]
                path_parts.pop(0)
                return handle_double_dots(should_parents)

        handle_double_dots(current_path)

        if not path_parts:
            return should_parents

        if path_parts[0] == ".":
            # если требуется начать с нынешней директории
            should_parents = current_path
            path_parts.pop(0)
            if not path_parts:
                return should_parents

        path_parts = path_parts[::-1]

        if not check_file:
            list_id = FileManager.look_for_file(name=path_parts[0], mime_type="application/vnd.google-apps.folder")
        else:
            list_id = FileManager.look_for_file(name=path_parts[0])

        if not list_id:
            return None

        # проверяем все папки с именем куда мы должны переместиться
        for parent_id in list_id:
            if check_parents(parent_id, 1):
                return parent_id

        return None

    @staticmethod
    def pwd(current_path_id: str):
        """
        Возвращает текущий путь от корня до текущей папки.

        Args:
            current_path_id (str): Идентификатор текущей папки.

        Returns:
            str: Полный путь от корня до текущей папки.
        """
        new_path = []

        def check_parents(parents_id):
            """Функция для заполнения пути начиная с последней директории вплоть до корня"""
            # Получаем данные о родительской папке
            post_path = FileManager.get_file_metadata(parents_id)

            try:
                # Выделяем идентификатор родительской папки для род. папки
                post_path_id = post_path["parents"][0]
            except (KeyError, IndexError):
                return

            # Выделяем имя и записываем
            name_post_path = FileManager.look_for_file(file_id=parents_id)
            new_path.append(name_post_path)

            # Рекурсивно вызываем функцию для родительской папки
            check_parents(parents_id=post_path_id)

        check_parents(current_path_id)

        if new_path:
            # Обратный порядок, так как мы шли от текущей папки к корневой
            new_path.reverse()
            # Соединяем элементы списка в строку
            return "MyDrive/" + "/".join(new_path) + "/"
        else:
            return "MyDrive/"

    @staticmethod
    def gather_needed_paths(path: str):
        """
        Выделяет все возможные пути, которые не существуют.

        Args:
            path (str): Путь, который нужно проверить.
            current_path (str): Текущий путь.

        Returns:
            dict: Словарь с ключами 'start_path' и 'paths_to_create'.
        """
        start_path = None
        path_to_create = []

        def check_path_parts(path_parts):
            nonlocal start_path, path_to_create
            start_path = PathNavigator.validate_path(path_parts, GoogleCloudTerminal.current_path)

            if start_path:
                return True

            path_to_create.append(path_parts)

            path_parts = re.sub('\n', "", path_parts)

            path_parts = path_parts.strip("/").split("/")

            path_parts = "/".join(path_parts[:-1])

            check_path_parts(path_parts)

        check_path_parts(path)

        if not start_path:
            return None

        return {"start_path": start_path, "path_to_create": path_to_create[::-1]}

    @staticmethod
    def gather_structure(source_id: str):
        """
        Выделяет всю ветку начная с файла source и заканчивая всеми путями исходящими из него.

        Args:
            source_id (str): Файл, с которого начнается выделяемая ветка.

        Returns:
            lisе: список файлов в СТРОГОЙ послдеовательности для копирования.
                    "?" - сигнал о заврешении ветки в пути. Надо сделать шаг назад:
                            присваиваем destination_id ид папки, сразу после "?"
                    "!" - сигнал о начале ветки в пути. Надо сделать шаг вперед:
                            присваиваем destination_id ид родительской папки текщуей папки.
        """

        all_files = FileManager.get_list_of_files(called_directly=False)

        subfiles = []

        for file in all_files:
            if 'parents' in file and file['parents'][0] == source_id:
                if file['mimeType'] == 'application/vnd.google-apps.folder':
                    # ОЧень похоже на поиск в глубину (алгоритм DFS)
                    subfiles = (subfiles + ["!"] + [file] +
                                PathNavigator.gather_structure(file['id']) + ["!"])
                else:
                    subfiles.append(file)

        return subfiles

    @staticmethod
    def get_child_files(source_id: str):
        """
        Выделяет все файлы лежащие в source_id

        Args:
            source_id (str): Родительская папка.

        Returns:
            list_child: список файлов находящихся в каталоге source_id.
        """
        all_files = FileManager.get_list_of_files(called_directly=False)
        list_child = []

        for file in all_files:
            if 'parents' in file and file['parents'][0] == source_id:
                list_child.append(file)

        return list_child


class CommandParser:
    """
    Класс для разбора и обработки команд, введенных пользователем.

    Этот класс содержит методы для аргументов команд,
    а также для обработки ошибок, связанных с неправильными аргументами.
    """
    @staticmethod
    def parser_command(input_string):
        """
        Разбирает строку команды и возвращает соответствующую команду и её аргументы.

        Args:
            input_string (str): Строка команды, введенная пользователем.

        Returns:
            tuple: Кортеж, содержащий команду (str) и разобранные аргументы (Namespace) или (None, None), если команда не распознана.

        """
        import shlex

        # словарь с командами и их парсерами
        commands = {
            'ls': CommandParser.parse_args_ls,
            'cd': CommandParser.parse_args_cd,
            'mkdir': CommandParser.parse_args_mkdir,
            'cp': CommandParser.parse_args_cp,
            'rm': CommandParser.parse_args_rm,
        }

        parts = shlex.split(input_string)  # Используем shlex для разбора строки

        if not parts:
            return None, None

        command = parts[0]
        args = parts[1:]

        if command in command:
            return command, commands[command](args)
        else:
            print(f"Unknown command: {command}")
            return None, None

    @staticmethod
    def parse_args_ls(args):
        """
        Парсер команды 'ls'. В дальнейшем документироваться не будет,
            так как структура для всез одна и та же

        Args:
            args (list): Список аргументов для команды 'ls'.

        Returns:
            Namespace: Разобранные аргументы или None,
                                если произошла ошибка или был запрошен help.
        """
        parser = argparse.ArgumentParser(description="List files in the specified directory. ")
        parser.add_argument('path', nargs="?", default=None, help='Path to list')
        parser.add_argument('-l', '--long', action='store_true', help="Use a long listing format")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return None

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            print(e)
            return None

    @staticmethod
    def parse_args_cd(args):
        parser = argparse.ArgumentParser(description="Change directory.")
        parser.add_argument('path', help="Path to change to")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return None

            return parser.parse_args(args)

        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            print(e)
            return None

    @staticmethod
    def parse_args_mkdir(args):
        parser = argparse.ArgumentParser(description="Create a new directory. ")
        parser.add_argument('path', nargs="+", default=None, help='Path to the new directory. ')
        parser.add_argument('-p', '--parents', action='store_true', help="Make parents directories as needed. ")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return None

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            print(e)
            return None

    @staticmethod
    def parse_args_cp(args):
        parser = argparse.ArgumentParser(description="Copy file from source to destination. ")
        parser.add_argument('source', nargs="?", default=None, help='Path file that needs copy. ')
        parser.add_argument('destination', nargs="?", default=None, help='Where to copy file. ')
        parser.add_argument('-r', '--recursive', action='store_true', help="The need to recursively copy the contents of the directory. ")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return None

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            print(e)
            return None

    @staticmethod
    def parse_args_rm(args):
        parser = argparse.ArgumentParser(description="Remove file from source to destination. ")
        parser.add_argument('path', nargs="?", default=None, help='Path file that needs delete. ')
        parser.add_argument('-r', '--recursive', action='store_true', help="Recursively delete the contents of the directory. ")
        parser.add_argument('-v', '--verbose', action='store_true', help="Show information about remove files. ")
        parser.add_argument("-i", '--interactive', action='store_true', help="Prompt before every removal.")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return None

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            print(f'Error when parse args command rm: {e}')
            return None


class UserInterface:
    def __init__(self):
        pass

    def show_message(self, message):
        sys.stdout.write(message + '\n')

    def show_error(self, error_message):
        sys.stdout.write(error_message + '\n')

    def show_success(self, success_message):
        sys.stdout.write(success_message + '\n')

    def request_input(self, prompt):
        return sys.stdin.readlines(prompt)


if __name__ == '__main__':
    # cp ./folder1 ./ -r
    # rm "./Copy of folder1" -r

    terminal = GoogleCloudTerminal()

    sys.stdout.write(f'{PathNavigator.pwd(terminal.current_path)} $ ')

    while True:
        input_string = sys.stdin.readline()

        print(terminal.execute_command(input_string))

        sys.stdout.write(f'{PathNavigator.pwd(terminal.current_path)} $ ')