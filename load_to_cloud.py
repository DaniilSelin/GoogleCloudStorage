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

def get_list_of_file(creds, called_directly=True):
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
        'pageSize': 10  # Максимальное количество файлов, которое нужно вернуть
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
                    print(file['name'])

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
            return root_folber
        print('Create folber compleate')
    else:
        print(f'error when creating folber: {response.status_code} - {response.text}')
        return None

def root_folber(creds):
    """
    Функция для поиска идентификатора корневой папки "LoadCloud" на Google Диске.
    Не подразумевает вызова напрямую

    Args:
        creds (Credentials): Учетные данные для аутентификации в Google API.

    Returns:
        str: Идентификатор корневой папки "LoadCloud" или создает новую папку, если не найдена.
    """
    files = get_list_of_file(creds, called_directly= False)

    if files is None:
        # Обработка случая, когда generator равен None
        return mkdir(creds, root=1)

    # Ищем на диске корневую папку
    for file in files:
        if file['name'] == "LoadCloud":
            return file['id']

    # если корневая папка не была наудена, просто создаем её
    return mkdir(creds, root=1)

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
