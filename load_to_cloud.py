import os
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
import requests
from requests import Response

SCOPES = ['https://www.googleapis.com/auth/drive']

def get_file_metadata(creds, file_id):
    """
    Получение метаданных файла по его идентификатору. Работет лучше чем мой поиск по идентификатору

    Args:
        creds: Учетные данные для авторизации.
        file_id: Идентификатор файла.

    Returns:
        dict: Метаданные файла (включая идентификаторы родительских папок).
    """
    headers = {
        'Authorization': f'Bearer {creds.token}',
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
        print(f'Failed to get file metadata. Status code: {response.status_code}')
        return None

def get_list_of_files(creds, called_directly=True):
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
        'Authorization': f'Bearer {creds.token}'
    }

    # URL запроса для получения списка файлов Google Drive API v3
    url = 'https://www.googleapis.com/drive/v3/files'

    # Параметры запроса
    params = {
        "corpora": "user",
        'fields': 'files(name, id)',
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
            return look_for_file(creds,"LoadCloud")
        print('Create folber compleate')
    else:
        print(f'error when creating folber: {response.status_code} - {response.text}')
        return None

def validate_path(creds, path, current_file=None):
    path = path.split("/")
    should_parents = None

    def check_parents(parents_id, index=1):
        """функция для углубления в родителя до корневой папки"""

        if path[index] == "":
            return True

        # получаем данные о родительской папке
        post_path = get_file_metadata(creds, parents_id)
        # выделяем идентификатор родительской папки для род. папки
        post_path_id = post_path["parents"][0]
        # выделяем имя
        name_post_path = look_for_file(creds, file_id=post_path_id)

        if name_post_path != path[index]:
            # если имя не совпало с ожидаемым, значит не тот идентификатор
            return False
        else:
            # если совпало с ожиданиями, продолжаем углубляться
            return check_parents(parents_id=post_path_id, index=index+1)

    def double_point(should_parents_f):
        if path[0] == "..":
            # выделяем
            should_parents_f_new = get_file_metadata(creds, should_parents_f)
            should_parents_f_new = should_parents_f_new["parents"][0]
            path.pop(0)
            return double_point(should_parents_f_new)
        else:
            return should_parents_f

    if path[0] == "..":
        should_parents = get_file_metadata(creds, current_file)
        should_parents = should_parents["parents"][0]

    should_parents = double_point(should_parents)

    if path[0] == ".":
        should_parents = get_file_metadata(creds, current_file)
        should_parents = should_parents["parents"][0]
        path.pop(0)

    if path[0] == "":
        return should_parents

    # переворачиваем наш путь, чтобы начать с конца
    path = path[::-1]

    if should_parents:
        path.append(look_for_file(creds, file_id=should_parents))
        path.append("")
    else:
        if not "" in path:
            path.append("")


    list_parents_id = look_for_file(creds, path[0])

    for _ in list_parents_id:
        if check_parents(_):
            print(f'Parrents path id is {_}')
            return _

def copy(creds, file_id: str, path: str):
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
        parents = validate_path(creds, path, file_id)

        if not parents:
            print("Enter path is incorrect, try again")
            return False

        body = {
            "parents": [f'{parents}'],
        }

    # Создаем заголовок с авторизационным токеном
    headers = {
        'Authorization': f'Bearer {creds.token}',
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

def find_file_by_id(files, folder_id: str):
    """
    Функция для поиска папки по идентификатору.

    Args:
        files (list): Список файлов на Google Диске.
        folder_id (str): Идентификатор папки для поиска.

    Returns:
        str: Имя папки с заданным идентификатором или None, если не найдена.
    """
    for file in files:
        if file['id'] == folder_id:
            return file['name']
    return None

def find_file_by_name(files, name: str):
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
    for file in files:
        if file['name'] == name:
            files_list_id.append(file['id'])

    return files_list_id if files_list_id else None

def look_for_file(creds, name: str=None, file_id: str=None, mime_type: str=None):
    """
    Функция для поиска файла на Google Диске по имени или идентификатору.

    Args:
        creds (Credentials): Учетные данные для аутентификации в Google API.
        name (str, optional): Имя файла для поиска. По умолчанию None.
        file_id (str, optional): Идентификатор файла для поиска. По умолчанию None.

    Returns:
        str: Идентификатор или имя файла.
    """
    files = get_list_of_files(creds, called_directly=False)

    if file_id:
        file_name = find_file_by_id(files, file_id)
        if file_name:
            return file_name
        else:
            print(f'File with ID "{file_id}" not found.')

    if name:
        file_id = find_file_by_name(files, name)
        if file_id:
            return file_id
        else:
            print(f'File with name "{name}" not found.')

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

def authorization() -> Credentials:
    """
    Функция для регистрации Google Drive API v3.
    Если пользователь не дал разрешения моему ПО, то кидает на регистрацю

    Returns:
        creds (Credentials): Учетные данные для аутентификации в Google API.
    """
    creds = None
    # Файл token.json хранит учетные данные пользователя и обновляет его автоматически, через запрос (Request)
    if os.path.exists('token.json'):
        # статический метод класса, который создает экземпляр учетных данных из файла json
        creds = Credentials.from_authorized_user_file('token.json')
    # Если нет действительных учетных данных, авторизуйте пользователя.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                # если creds != None и учетные данные просрочились, просто обновляем их запросом
                creds.refresh(Request())
            except RefreshError:
                # Если не удалось обновить токен, удаляем token.json и повторяем авторизацию
                os.remove('token.json')
                creds = None

        if not creds:
            # создаем поток авторизации, то бишь получаем от имени моего ПО данные для авторизации в диске юзера
            # собственно данные проекта, приложение, меня как разработчика лежат в credentials
            # потом сразу пускаем на выбранном ОС порте (порт=0) сервер для прослушивания ответа от потока авторизации
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes= SCOPES)
            creds = flow.run_local_server(port=0)
            # Сохраните учетные данные для следующего запуска.
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

    return creds

if __name__ == '__main__':
    creds = authorization()
    #root_folber(creds)
    #get_list_of_file(creds)
    #mkdir(creds)
    path1 = "/home/vboxuser/Python"
    path2 = "./vboxuser/Python"
    path3 = "../"
    path = "LoadCloud"
    print(validate_path(creds,path))
    #file = copy(creds, "1jxgUUdzzB9UHdEJnt5u0cOe4mF1oOw6Ksw1uDmgtDp4", path)
    #remove(creds, file["id"])