import os
import sys
from typing import Any
import argparse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
import requests
from requests import Response

SCOPES = ['https://www.googleapis.com/auth/drive']

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
        self.token_path = token_path
        self.credentials_path = credentials_path

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

    def change_directory(self, path_new):
        """
        Изменяет текущий рабочий каталог на указанный путь, если он существует.

        Args:
            path_new (str): Новый путь для перехода.
        """
        try:
            new_path = PathNavigator.validate_path(path=path_new, current_path=GoogleCloudTerminal.current_path)

            if new_path:
                GoogleCloudTerminal.current_path = new_path
        except Exception:
            print("Error: New path is incorrect")


class FileManager:

    @staticmethod
    def get_user_drive_id():
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
        Получение метаданных файла по его идентификатору. Работет лучше чем мой поиск по идентификатору

        Args:
            creds: Учетные данные для авторизации.
            file_id: Идентификатор файла.

        Returns:
            dict: Метаданные файла (включая идентификаторы родительских папок).
        """
        headers = {
            'Authorization': f'Bearer {GoogleCloudTerminal.creds.token}',
            'Content-Type': 'application/json'
        }

        url = f'https://www.googleapis.com/drive/v3/files/{file_id}'
        params = {
            'fields': 'name, id, parents'
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

        files = FileManager.get_list_of_files(called_directly=False)

        if path:
            path_parts_id = PathNavigator.validate_path(path=path, current_path=GoogleCloudTerminal.current_path)
        else:
            path_parts_id = GoogleCloudTerminal.current_path


        for file in files:
            if 'parents' in file and file['parents'] == path_parts_id:
                if show_long:
                    print(file['name'], " ", file['id'], " ", file['mimeType'])
                else:
                    print(file['name'])

    @staticmethod
    def parse_args_ls(args):
        parser = argparse.ArgumentParser(description="List files in the specified directory. ")
        parser.add_argument('path', nargs="?", default=None, help='Path to list')
        parser.add_argument('-l', '--long', action='store_true', help="Use a long listing format")
        options = parser.parse_args(args)

        # Проверка на наличие --help или -h
        if '--help' in args or '-h' in args:
            try:
                parser.print_help()
            # не дать боярину стопнуть программу
            except SystemExit:
                pass

        return options

    @staticmethod
    def mkdir(creds, root=False):
        """
        Функция для осздания папки в Google Drive.

        Args:
            creds (Credentials): Учетные данные для аутентификации в Google API.
            root (bool, optional): Флаг, указывающий, что функция вызвана для создания корневой папки.
                                            По умолчанию False.

        Returns:
            function: Вызываем функцию описка корневой еще раз.
                    Возвращает None в случае ошибки.
        """
        # Создаем заголовок с авторизационным токеном
        headers = {
            'Authorization': f'Bearer {creds.token}'
        }

        # URL запроса для получения списка файлов Google Drive API v3
        url = 'https://www.googleapis.com/drive/v3/files'

        body = {
            "name": "LoadCloud",
            "mimeType": "application/vnd.google-apps.folder",
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            if root:
                print("root folber not found, i will try create root folber")
                print('Create folber compleate')
                return FileManager.look_for_file("LoadCloud")
            print('Create folber compleate')
        else:
            print(f'error when creating folber: {response.status_code} - {response.text}')
            return None

    @staticmethod
    def touch(path):
        # Метод для создания файла в Google Cloud
        pass

    @staticmethod
    def copy(file_id: str, path: str):
        """
        Функция для создания копии файла в Google Drive.
        Args:
        creds: Учетные данные для авторизации.
        file_id: Идентификатор файла, который нужно скопировать.
        path: место куда копировать наш файл, вот шаблон
            "./path" - начиная с нынешней директории
            "../" - начная с родительско директории
            "/"- путь начиная с корня
            Указание пути необходимо, так как в разным папках может находится майлы/папки
            с одинаковыми именами!!!
        Returns: Информация о созданной копии файла.
        """

        if path == "/":
            body = {
                "parents": ['root'],
            }
        else:
            parents = PathNavigator.validate_path(path, file_id)

            if not parents:
                print("Enter path is incorrect, try again")
                return False

            body = {
                "parents": [f'{parents}'],
            }

        # Создаем заголовок с авторизационным токеном
        headers = {
            'Authorization': f'Bearer {GoogleCloudTerminal.creds.token}',
            'Content-Type': 'application/json',
        }

        # URL запроса для копирования файла Google Drive API v3
        url = f'https://www.googleapis.com/drive/v3/files/{file_id}/copy'

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            # Обработка успешного ответа
            file_info = response.json()
            print('File copied successfully.')
            print('File ID:', file_info['id'])
            print('File Name:', file_info['name'])
            return file_info
        else:
            # Обработка ошибки
            try:
                error_message = response.json()
            except ValueError:
                error_message = response.text
            print('Failed to copy file. Status code:', response.status_code)
            print('Error message:', error_message)
            return None

    @staticmethod
    def remove(creds, file_id):
        headers = {
            'Authorization': f'Bearer {creds.token}'
        }

        # URL запроса для удаления файла Google Drive API v3
        url = f'https://www.googleapis.com/drive/v3/files/{file_id}'

        response = requests.delete(url, headers=headers)

        if response.status_code == 204:
            print('Delete compleate')
        else:
            print(f'error when deleting file: {response.status_code} - {response.text}')
            return None

class PathNavigator:
    @staticmethod
    def validate_path(path, current_path=GoogleCloudTerminal.current_path):
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

            if post_path_id == should_parents:
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

        list_id = FileManager.look_for_file(name=path_parts[0], mime_type="application/vnd.google-apps.folder")

        # проверяем все папки с именем куда мы должны переместиться
        for parent_id in list_id:
            if check_parents(parent_id, 1):
                return parent_id

        return None

    @staticmethod
    def pwd(current_path_id):
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
    def parse_path(path):
        # Метод для разбора пути и получения идентификаторов папок и файлов
        pass

    @staticmethod
    def navigate_to_directory(self, path):
        # Метод для навигации по структуре папок
        pass

    @staticmethod
    def find_file_by_path(self,path):
        # Метод для поиска файла по указанному пути
        pass

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
    terminal = GoogleCloudTerminal()


    terminal.change_directory("./LoadCloud")
    terminal.change_directory('./folber2')
    print("ur part path is ", PathNavigator.pwd(terminal.current_path))
    while True:

        ls = sys.stdin.readline().split()

        args = ls

        parsed_args = FileManager.parse_args_ls(args)
        print(parsed_args.path, parsed_args.long)
        FileManager.ls(parsed_args.path, parsed_args.long)

        sys.stdout.write(f'{PathNavigator.pwd(terminal.current_path)} $ ')