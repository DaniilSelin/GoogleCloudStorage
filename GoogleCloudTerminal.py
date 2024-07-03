from CommandParser import CommandParser
from FileManager import FileManager
from PathNavigator import PathNavigator
from UserInterface import UserInterface

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

        # авто запуск авторизации
        self._autorization()

        UserInterface.show_message([
                 {'text': "I'm determining the ID of your GoogleDrive... ", 'color': 'bright_yellow'}
        ])
        stop_loading = UserInterface.show_loading_message([{"text": "Definition is complete", "color": "green"}])
        # получаем идентификатор драйвера пользователя
        user_drive_id = FileManager.get_user_drive_id()
        if user_drive_id:
            os.environ["GOOGLE_CLOUD_MY_DRIVE_ID"] = user_drive_id
            os.environ["GOOGLE_CLOUD_CURRENT_PATH"] = user_drive_id
            stop_loading()
        else:
            UserInterface.show_error([
                {'text': 'Failed to retrieve user drive ID. ', 'color': 'red'},
                {'text': 'Please delete your token.json and reauthorize', 'color': 'yellow', "clear": "\n"}]
                                     )

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
        UserInterface.show_message(
            [{'text': 'Starting authorization process...', 'color': 'bright_yellow'}]
        )
        stop_loading = UserInterface.show_loading_message()

        # Файл token.json хранит учетные данные пользователя и обновляет его автоматически, через запрос (Request)
        if os.path.exists(self.token_path):
            # статический метод класса, который создает экземпляр учетных данных из файла json
            # сразу сериализуем этот объект и кидаем его в переменную окружения
            UserInterface.show_message(
                            [{'text': 'Found existing token file. Loading credentials...', 'color': 'bright_yellow'}]
            )
            os.environ["GOOGLE_CLOUD_CREDS"] = Credentials.from_authorized_user_file(self.token_path).to_json()

        # Если нет действительных учетных данных, авторизуйте пользователя.
        if not self._creds or not self._creds.valid:
            if self._creds and self._creds.expired and self._creds.refresh_token:
                try:
                    # если creds != None и учетные данные просрочились, просто обновляем их запросом
                    UserInterface.show_message(
                        [{'text': "Refreshing expired credentials...", 'color': 'bright_yellow'}]
                    )
                    refresh_creds = self._creds
                    refresh_creds.refresh(Request())
                    os.environ["GOOGLE_CLOUD_CREDS"] = refresh_creds.to_json()
                except RefreshError:
                    # Если не удалось обновить токен, удаляем token.json и повторяем авторизацию
                    UserInterface.show_error(
                        [{'text': "Failed to refresh credentials. Reauthorizing...", 'color': 'red'}]
                    )
                    os.remove(self.token_path)
                    os.environ["GOOGLE_CLOUD_CREDS"] = ""

            if not self._creds:
                UserInterface.show_message(
                    [{'text': "No valid credentials found. Starting new authorization...", 'color': 'bright_yellow'}]
                )
                # Читаем содержимое файла credentials.json
                with open(self.credentials_path) as f:
                    try:
                        cred_check = json.load(f)
                    except json.JSONDecodeError as e:
                        UserInterface.show_error(
                            "Credentials not found, trying to decrypt them."
                        )
                        from encryption import decrypt_credentials

                        if decrypt_credentials.decrypt("encryption"):
                            UserInterface.show_success(
                                "Credentials have been created. Continuing authorization process."
                            )
                # создаем поток авторизации, то бишь получаем от имени моего ПО данные для авторизации в диске юзера
                # собственно данные проекта, приложение, меня как разработчика лежат в credentials
                # потом сразу пускаем на выбранном ОС порте (порт=0) сервер для прослушивания ответа от потока авторизации
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, scopes=SCOPES)
                os.environ["GOOGLE_CLOUD_CREDS"] = flow.run_local_server(port=0).to_json()
                # Сохраните учетные данные для следующего запуска.
                with open(self.token_path, 'w') as token:
                    token.write(os.getenv("GOOGLE_CLOUD_CREDS"))
                UserInterface.show_success("Authorization successful. Credentials saved. ")
                stop_loading()
            elif self._creds.valid:
                UserInterface.show_success("Authorization successful. ")
                stop_loading()
        else:
            UserInterface.show_success("Authorization successful. ")
            stop_loading()

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
        elif command == 'ren':
            return self.rename(args)
        elif command == "trash":
            return self.trash(args)
        elif command == "restore":
            return self.restore(args)
        elif command == "emptyTrash":
            return self.empty_trash()
        else:
            UserInterface.show_error(
                f"Unknown command {command}"
            )

    def change_directory(self, args):
        """
        Изменяет текущий рабочий каталог на указанный путь, если он существует.

        Args:
            path_new (str): Новый путь для перехода.
        """
        try:
            new_path = PathNavigator.validate_path(path=args.path, current_path=os.getenv("GOOGLE_CLOUD_CURRENT_PATH"))

            if new_path:
                os.environ["GOOGLE_CLOUD_CURRENT_PATH"] = new_path
                return new_path
            else:
                UserInterface.show_error(
                    f"Error: New path is incorrect"
                )
        except Exception as e:
            UserInterface.show_error(
                f"Incorrect use of the command caused the message. Called exception: {e}"
            )

    def list_files(self, args):
        """
        Метод для вывода списка файлов в текущем каталоге.
        Args:
            args: Аргументы для команды 'ls'.
        """
        try:
            return FileManager.ls(path=args.path, show_long=args.long)

        except Exception as e:
            UserInterface.show_error(
                f"Incorrect use of the command caused the message. Called exception: {e}"
            )

    def make_directory(self, args):
        """
        Метод для создания директории
        Args:
            args: Аргументы для команды 'mkdir'.
        """
        try:
            return FileManager.mkdir(path=args.path[0], create_parents=args.parents)
        except Exception as e:
            UserInterface.show_error(
                f"Incorrect use of the command caused the message. Called exception: {e}"
            )

    def copy(self, args):
        """
        Метод для копирования файлов/директорий
        Args:
            args: Аргументы для команды 'cp'.
        """
        try:
            FileManager.cp(source=args.source, destination=args.destination, recursive=args.recursive)
        except Exception as e:
            UserInterface.show_error(
                f"Incorrect use of the command caused the message. Called exception: {e}"
            )

    def remove(self, args):
        """
        Метод для удаления файлов/директорий
        Args:
            args: Аргументы для команды 'rm'.
        """
        try:
            FileManager.rm(path=args.path, recursive=args.recursive, verbose=args.verbose, interactive=args.interactive)
        except Exception as e:
            UserInterface.show_error(
                f"Incorrect use of the command caused the message. Called exception: {e}"
            )

    def touch(self, args):
        """
        Метод для создания файлов
        Args:
            args: Аргументы для команды 'touch'.
        """
        try:
            FileManager.touch(path=args.path,
                            mimeType=args.mimeType,
                            time_modification=args.modification,
                            verbose=args.verbose
                            )
        except Exception as e:
            UserInterface.show_error(
                f"Incorrect use of the command caused the message. Called exception: {e}"
            )

    def move(self, args):
        """
        Метод для перемещения файла
        Args:
            args: Аргументы для команды 'mv'.
        """
        try:
            FileManager.mv(
                source_path=args.source_path,
                destination_path=args.destination_path
            )
        except Exception as e:
            UserInterface.show_error(
                f"Incorrect use of the command caused the message. Called exception: {e}"
            )

    def rename(self, args):
        """
        Метод для переименования файла, реализована Perl-версия rename.
        Args:
            args: Аргументы для команды 'mv'.
        """
        try:
            FileManager.ren(
                perl_expression=args.perl_expression,
                pattern_file=args.pattern_file
            )
        except Exception as e:
            UserInterface.show_error(
                f"Incorrect use of the command caused the message. Called exception: {e}"
            )

    def mimeType(self):
        """
        Метод для перемещения файла
        """
        try:
            FileManager.mimeType()
        except Exception as e:
            UserInterface.show_error(
                f"Incorrect use of the command caused the message. Called exception: {e}"
            )

    def trash(self, args):
        """
        Функция для перемещения файла в корзину.
        Args:
            args: Аргументы для команды 'trash'.
        """
        try:
            FileManager.trash(args.path)
        except Exception as e:
            UserInterface.show_error(
                f"Incorrect use of the command caused the message. Called exception: {e}"
            )

    def restore(self, args):
        """
        Функция для восстановления файла из корзины.
        Args:
            args: Аргументы для команды 'restore'.
        """
        try:
            FileManager.restore(args.path)
        except Exception as e:
            UserInterface.show_error(
                f"Incorrect use of the command caused the message. Called exception: {e}"
            )

    def empty_trash(self):
        try:
            FileManager.empty_trash()
        except Exception as e:
            UserInterface.show_error(
                f"Incorrect use of the command caused the message. Called exception: {e}"
            )

# ren "" *txt

if __name__ == '__main__':
    # mv ./file ./folder1

    terminal = GoogleCloudTerminal()

    sys.stdout.write(f'{PathNavigator.pwd(os.getenv("GOOGLE_CLOUD_CURRENT_PATH"))} $ ')

    while True:
        input_string = sys.stdin.readline()

        terminal.execute_command(input_string)

        sys.stdout.write(f'{PathNavigator.pwd(os.getenv("GOOGLE_CLOUD_CURRENT_PATH"))} $ ')