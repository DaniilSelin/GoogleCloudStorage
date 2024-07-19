import requests
import os
import json
from google.oauth2.credentials import Credentials
from UserInterface import UserInterface


class FileManagerProxy:
    """ Класс дублирующий методы FileManager для класса PathNavigator

    Нужды в нем появилась из за зацикливания импортов"""
    @staticmethod
    def _creds():
        """ Восстанваливаем объект после сериализаци """
        return Credentials.from_authorized_user_info(
            json.loads(os.getenv("GOOGLE_CLOUD_CREDS")))

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
            'Authorization': f'Bearer {FileManagerProxy._creds().token}'
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
                # Класс вобще не долен затрагиваться пользователем
                pass

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
            'Authorization': f'Bearer {FileManagerProxy._creds().token}',
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
            UserInterface.show_error(
                f'Failed to get file metadata. Status code: {response.status_code}'
            )
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
        files = FileManagerProxy.get_list_of_files(called_directly=False)

        if file_id:
            file_name = FileManagerProxy.find_file_by_id(files, file_id, mime_type)
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
            file_id = FileManagerProxy.find_file_by_name(files, name, mime_type)
            if file_id:
                return file_id
            else:
                UserInterface.show_error(
                    f'File with name "{name}" not found.'
                )
                return None
