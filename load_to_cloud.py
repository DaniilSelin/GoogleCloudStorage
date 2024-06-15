import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def main():
    """Показывает список файлов на Google Диске"""
    creds = None
    # Файл token.json хранит учетные данные пользователя и обновляет его автоматически, через запрос (Request)
    if os.path.exists('token.json'):
        # статический метод класса, кторорый создает экземпляр учетных данных из файла json
        creds = Credentials.from_authorized_user_file('token.json')
    # Если нет действительных учетных данных, авторизуйте пользователя.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # если credits!=None и учетные данные просрочились, просто оновляем их гет запросом
            # Request() - вызываем статический статический метод __call__, который возвращает HTTP запрос вроеж
            # который неободим для обновления токена доступа
            creds.refresh(Request())
        else:
            # создаем поток авторизации, то бишь получаем от имени моего ПО данные для атворищзации в диске юзера
            # собса данные проекта, приложение, меня как разработчика лежат в credintails
            # потом сразу пускаем на выбранном ОС порте(порт=0) сервер для прослешивания ответа от потока авторизации
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json')
            creds = flow.run_local_server(port=0)
        # Сохраните учетные данные для следующего запуска.
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # инициализируеем нашу апишку, для доступа к гугл доксу юзера.
    service = build('drive', 'v3', credentials=creds)

    # Вызов Google Drive API.
    results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(f'{item["name"]} ({item["id"]})')


if __name__ == '__main__':
    main()