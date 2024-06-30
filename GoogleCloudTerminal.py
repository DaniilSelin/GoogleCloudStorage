from CommandParser import CommandParser
from FileManager import FileManager
from PathNavigator import PathNavigator

import os
import sys
import json
import dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError


SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleCloudTerminal:
    """
    Основной класс для связи между UserInterface и FileManager

    Этот класс содержит отвечает за авторизацию пользователя,
    Вызывает нужный метод из FileManager в зависимости от сообщение UserInterface
    """

    def __init__(self, token_path="encryption/token.json", credentials_path="encryption/credentials.json"):
        """
        Инициализирует GoogleCloudTerminal, устанавливает текущий путь и запускает авторизацию.

        Args:
            token_path (str): Путь к файлу токена.
            credentials_path (str): Путь к файлу учетных данных.
        """
        # Чтобы это работало и на винде, подходи м к файлам по абсолютному пути
        self.token_path = os.path.join(os.path.dirname(__file__), token_path)
        self.credentials_path = os.path.join(os.path.dirname(__file__), credentials_path)

        #авто запуск авторизации
        self._autorization()
        #получаем идентификатор драйвера пользователя
        os.environ["GOOGLE_CLOUD_MY_DRIVE_ID"] = FileManager.get_user_drive_id()
        os.environ["GOOGLE_CLOUD_CURRENT_PATH"] = FileManager.get_user_drive_id()

    @property
    def _creds(self):
        """ Восстанваливаем объект после сериализаци """
        if not os.getenv("GOOGLE_CLOUD_CREDS"):
            return None
        return Credentials.from_authorized_user_info(
            json.loads(os.getenv("GOOGLE_CLOUD_CREDS")))

    def _autorization(self):
        """
            Функция для регистрации Google Drive API v3.
            Если пользователь не дал разрешения моему ПО, то кидает на регистрацю
        """
        # Файл token.json хранит учетные данные пользователя и обновляет его автоматически, через запрос (Request)
        if os.path.exists(self.token_path):
            # статический метод класса, который создает экземпляр учетных данных из файла json
            # сразу сериализуем этот объект и кидаем его в переменную окружения
            os.environ["GOOGLE_CLOUD_CREDS"] = Credentials.from_authorized_user_file(self.token_path).to_json()
        # Если нет действительных учетных данных, авторизуйте пользователя.
        if not self._creds or not self._creds.valid:
            if self._creds and self._creds.expired and self._creds.refresh_token:
                try:
                    # если creds != None и учетные данные просрочились, просто обновляем их запросом
                    self._creds.refresh(Request())
                except RefreshError:
                    # Если не удалось обновить токен, удаляем token.json и повторяем авторизацию
                    os.remove(self.token_path)
                    os.environ["GOOGLE_CLOUD_CREDS"] = ""

            if not self._creds:
                # Читаем содержимое файла credentials.json
                with open(self.credentials_path) as f:
                    try:
                        cred_check = json.load(f)
                    except json.JSONDecodeError as e:
                        print(" Credentials not found, i trying decrypt them. ")
                        from encryption import decrypt_credentials

                        if decrypt_credentials.decrypt("encryption"):
                            print("Credentials have been created, we continue the authorization process. ")

                # создаем поток авторизации, то бишь получаем от имени моего ПО данные для авторизации в диске юзера
                # собственно данные проекта, приложение, меня как разработчика лежат в credentials
                # потом сразу пускаем на выбранном ОС порте (порт=0) сервер для прослушивания ответа от потока авторизации
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, scopes=SCOPES)
                os.environ["GOOGLE_CLOUD_CREDS"] = flow.run_local_server(port=0).to_json()
                # Сохраните учетные данные для следующего запуска.
                with open(self.token_path, 'w') as token:
                    token.write(os.getenv("GOOGLE_CLOUD_CREDS"))

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
        elif command == 'touch':
            return self.touch(args)
        elif command == 'mv':
            return self.move(args)
        elif command == 'mimeType':
            return self.mimeType()
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
        FileManager.cp(source=args.source, destination=args.destination, recursive=args.recursive)

    def remove(self, args):
        """
        Метод для удаления файлов/директорий
        Args:
            args: Аргументы для команды 'rm'.
        """
        FileManager.rm(path=args.path, recursive=args.recursive, verbose=args.verbose, interactive=args.interactive)

    def touch(self, args):
        """
        Метод для создания файлов
        Args:
            args: Аргументы для команды 'touch'.
        """
        FileManager.touch(path=args.path,
                          mimeType=args.mimeType,
                          time_modification=args.modification)

    def move(self, args):
        FileManager.mv(
            source_path=args.source_path,
            destination_path=args.destination_path
        )

    def mimeType(self):
        FileManager.mimeType()


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
    # mv ./file ./folder1

    terminal = GoogleCloudTerminal()

    sys.stdout.write(f'{PathNavigator.pwd(os.getenv("GOOGLE_CLOUD_CURRENT_PATH"))} $ ')

    while True:
        input_string = sys.stdin.readline()

        print(terminal.execute_command(input_string))

        sys.stdout.write(f'{PathNavigator.pwd(os.getenv("GOOGLE_CLOUD_CURRENT_PATH"))} $ ')