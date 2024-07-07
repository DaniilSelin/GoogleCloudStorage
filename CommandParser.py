import argparse
from UserInterface import UserInterface


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
            'touch': CommandParser.parse_args_touch,
            'mv': CommandParser.parse_args_mv,
            'ren': CommandParser.parse_args_ren,
            'trash': CommandParser.parse_args_trash,
            'restore': CommandParser.parse_args_restore,
            'mimeType': CommandParser.parse_args_mimeType,
            'emptyTrash': CommandParser.parse_args_empty_trash,
            'tree': CommandParser.parse_args_tree,
            'du': CommandParser.parse_args_du,
            'share': CommandParser.parse_args_share,
            'quota': CommandParser.parse_args_quota,
            'export': CommandParser.parse_args_export,
            'export_format': CommandParser.parse_args_export_format,
            'ChangeMime': CommandParser.parse_args_ChangeMime,
            'upload': CommandParser.parse_args_upload,
        }

        parts = shlex.split(input_string)  # Используем shlex для разбора строки

        if not parts:
            return None, None

        command = parts[0]
        args = parts[1:]

        if command in commands:
            return command, commands[command](args)
        else:
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
        parser.add_argument('pattern', nargs="?", default=None, help='Pattern for files that need to be display. Does not work without the path argument!')

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_cd(args):
        parser = argparse.ArgumentParser(description="Change directory.")
        parser.add_argument('path', help="Path to change to")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)

        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
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
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_cp(args):
        parser = argparse.ArgumentParser(description="Copy file from source to destination. ")
        parser.add_argument('source', nargs="?", default=None, help='Path file that needs copy. ')
        parser.add_argument('destination', nargs="?", default=None, help='Where to copy file. ')
        parser.add_argument('-r', '--recursive', action='store_true', help="The need to recursively copy the contents of the directory. ")
        parser.add_argument('--mimeType', default=None, type=str,
                            help="mimeType for search file (if some file have the same name....)")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_rm(args):
        parser = argparse.ArgumentParser(description="Remove file from source to destination. ")
        parser.add_argument('path', nargs="?", default=None, help='Path file that needs delete. ')
        parser.add_argument('-r', '--recursive', action='store_true', help="Recursively delete the contents of the directory. ")
        parser.add_argument('-v', '--verbose', action='store_true', help="Show information about remove files. ")
        parser.add_argument("-i", '--interactive', action='store_true', help="Prompt before every removal.")
        parser.add_argument('--mimeType', default=None, type=str,
                            help="mimeType for search file (if some file have the same name....)")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_touch(args):
        parser = argparse.ArgumentParser(description="Create file or update metadata file. ")
        parser.add_argument('path', nargs="?", default=None, help='Path file that needs create. ')
        parser.add_argument('-m', '--modification', action='store_true',
                            help="Update the modification time only. Exampl: 2024-06-28T15:30:00Z")
        parser.add_argument('-v', '--verbose', action='store_true',
                            help="Print information about the new files? ")
        parser.add_argument('--mimeType', type=str,
                            help="Specify the MIME type for the file being created. Format: --mimeType=<mime-type-string>. If u didn't know mimeType use command: mimeType")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_mv(args):
        parser = argparse.ArgumentParser(description="Move file from source to destination. ")
        parser.add_argument('source_path', nargs="?", default=None, help=' Where to move the file from. ')
        parser.add_argument('destination_path', nargs="?", default=None, help='where to move the file. ')
        parser.add_argument('--mimeType', default=None, type=str,
                            help="mimeType for search file (if some file have the same name....)")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_ren(args):
        parser = argparse.ArgumentParser(description="Rename files. ")
        parser.add_argument('perl_expression', nargs="?", default=None, help='Perl-expression for change name files. ')
        parser.add_argument('pattern_file', nargs="?", default=None, help='Pattern for search files that need to be rename. ')

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_mimeType(args):
        parser = argparse.ArgumentParser(description="Info adout mimeType and extension. ")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_trash(args):
        parser = argparse.ArgumentParser(description="Move file to trash. ")
        parser.add_argument('path', nargs="?", default=None, help='Path file that need move to trash. ')
        parser.add_argument('--mimeType', default=None, type=str,
                            help="mimeType for search file (if some file have the same name....)")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_restore(args):
        parser = argparse.ArgumentParser(description="Restore file from trash. ")
        parser.add_argument('path', nargs="?", default=None, help='Path file that need restore from trash. Path before moving to trash')
        parser.add_argument('--mimeType', default=None, type=str,
                            help="mimeType for search file (if some file have the same name....)")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_empty_trash(args):
        parser = argparse.ArgumentParser(description="Command for empty trash. ")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_tree(args):
        parser = argparse.ArgumentParser(description="Display the file structure as a tree. ")
        parser.add_argument('path', nargs="?", default=None, help='The directory from which to start displaying. ')
        parser.add_argument('-d', '--dirs_only', action='store_true',
                            help="List directories only. ")
        parser.add_argument('-i', '--no_indent', action='store_true',
                            help="Make tree not print the indentation lines. ")
        parser.add_argument('-s', '--size', action='store_true',
                            help="Print the size of each file in bytes. ")
        parser.add_argument('pattern', nargs="?", default=None, help='Pattern for files that need to be display. Does not work without the path argument!')

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_du(args):
        parser = argparse.ArgumentParser(description="Estimate file space usage.")
        parser.add_argument('path', nargs="?", default=None, help='The directory to start with.')
        parser.add_argument('-s', '--show_free_space', action='store_true', help="Display information only about users drive.")
        parser.add_argument('-a', '--all', action='store_true',
                            help="Write counts for all files, not just directories.")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_share(args):
        parser = argparse.ArgumentParser(description="Manage access and sharing settings for files and folders.")
        parser.add_argument('path', nargs="?", default=None, help='The path to the file or folder to share.')
        parser.add_argument('email', nargs="?", default=None, help='The email of the user to share with.')
        parser.add_argument('-r', '--role', default='reader', choices=['writer', 'commenter', 'reader', 'organizer', 'fileOrganizer'],
                            help='The role to assign to the user (writer, commenter, reader, organizer, fileOrganizer).')
        parser.add_argument('-t', '--type', default='user', choices=['user', 'group', 'domain', 'anyone', 'restricted'],
                            help='The type of access (user, group, domain, anyone, restricted (remove access to a user who has a link)). Default is user.')
        parser.add_argument('--mimeType', default=None, type=str,
                            help="mimeType for search file (if some file have the same name....)")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_quota(args):
        parser = argparse.ArgumentParser(description="Information about the Google Drive disk space quota. ")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_export(args):
        parser = argparse.ArgumentParser(
            description="Export a file from Google Drive to a specified format and save it locally.")
        parser.add_argument('path', nargs="?", default=None, help='The path to the file in Google Drive.')
        parser.add_argument('local_path', nargs="?", default="./", help='The local path to save the exported file.')
        parser.add_argument('-m', '--mimeType',
                            help='The MIME type to export the file as. If not specified, the original MIME type will be used.')

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_export_format(args):
        parser = argparse.ArgumentParser(
            description="Get supported export formats for a given MIME type in Google Drive.")
        parser.add_argument('path', nargs='?', default=None,
                            help='Optional path to the file in Google Drive to retrieve its MIME type.')
        parser.add_argument('-m', '--mimeType',
                            help='MIME type of the file for which export formats are requested.')

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_ChangeMime(args):
        parser = argparse.ArgumentParser(description="Change mimeType of file. ")
        parser.add_argument('path', nargs="?", default=None, help='Path to the file for which mimeType needs to be changed. ')
        parser.add_argument('new_mimeType', nargs="?", default=None, help='New mimeType for file->path. ')

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_upload(args):
        parser = argparse.ArgumentParser(description="Upload a file to Google Drive.")
        parser.add_argument('local_path', type=str, help="Local path to the file to upload.")
        parser.add_argument('path', type=str, default="./", help="Path in Google Drive where to upload.")
        parser.add_argument('--name', type=str, default=None, help="Optional name for the uploaded file.")
        parser.add_argument('--mimeType', type=str, default=None, help="Optional MIME type of the uploaded file. Or you can just specify the file extension in the name. ")
        parser.add_argument('--uploadType', type=str, choices=['SimpleUpload', 'MultipartUpload', 'ResumableUpload'],
                            default='SimpleUpload',
                            help="Type of upload method (SimpleUpload, MultipartUpload, ResumableUpload). Default is SimpleUpload")

        try:
            # Проверка на наличие --help или -h
            if '--help' in args or '-h' in args:
                parser.print_help()
                return "help"

            return parser.parse_args(args)
        except SystemExit:
            # Перехват SystemExit для предотвращения завершения программы
            # При вызове --help или -h, класс parser вызывает это исключение
            pass

        except argparse.ArgumentError as e:
            # Перехват ArgumentError для обработки ошибок неправильных аргументов
            UserInterface.show_error(e)
            return None
