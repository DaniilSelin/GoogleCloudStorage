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
                return None

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
                return None

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
            UserInterface.show_error(e)
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
                return None

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
                return None

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
                return None

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
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_restore(args):
        parser = argparse.ArgumentParser(description="Restore file from trash. ")
        parser.add_argument('path', nargs="?", default=None, help='Path file that need restore from trash. Path before moving to trash')

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
            UserInterface.show_error(e)
            return None

    @staticmethod
    def parse_args_empty_trash(args):
        parser = argparse.ArgumentParser(description="Command for empty trash. ")

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
            UserInterface.show_error(e)
            return None
