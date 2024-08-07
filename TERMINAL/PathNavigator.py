import re
import os
import readline
from FileManagerProxy import FileManagerProxy
from UserInterface import UserInterface


class PathNavigator:
    """
    Класс для навигации по GoogleDrive, содержит методы для работы с путями

        и выделением каких либо структур из драйвера.
    """
    COMMANDS = ['ls', 'cd', 'mkdir', 'cp', 'pattern_rm',
                'rm', 'touch', 'mv', 'ren', 'trash',
                'restore', 'mimeType', 'emptyTrash', 'tree', 'du',
                'share', 'quota', 'export', 'export_format', 'ChangeMime',
                'upload', 'sync'
                ]
    STRUCT = []

    @staticmethod
    def validate_path(path: str, current_path=os.getenv("GOOGLE_CLOUD_CURRENT_PATH"), check_file=False, mimeType=None):
        # ОПАСНО не указывать current_path напрямую, так как питон заполняет это поле,
        # базовым значением, которе мы указали в GCT.current_path = root
        """
        Проверяет и возвращает идентификатор каталога по указанному пути.

        Args:
            path (str): Путь для проверки.
            current_path (str): Текущий путь.
            check_file (bool): Включать файлы в зону поиска?
            mimeType (str): Сузить круг поиска до определенного mimeTyep.

        Returns:
            str or None: Идентификатор папки, если путь существует, иначе None.
        """
        import re

        path = re.sub('\n',"", path)

        path_parts = path.strip("/").split("/")

        # ожидаемый конечный родитель
        if path_parts[0] == "~":
            should_parents = os.getenv("GOOGLE_CLOUD_MY_DRIVE_ID")
            path_parts.pop(0)
            if not path_parts:
                return should_parents

        else:
            should_parents = current_path

        def check_parents(parents_id, path_index):
            """Рекурсивная функция для проверки каждого родителя до корневой папки"""
            post_path = FileManagerProxy.get_file_metadata(parents_id)

            # запрашиваем ид родителя
            post_path_id = post_path["parents"][0]

            if len(path_parts) == path_index:
                if post_path_id == should_parents:
                    return True
                else:
                    return None

            name_post_path = FileManagerProxy.look_for_file(file_id=post_path_id)

            # если именя родителя этого пути не совпал с ожидаемым, выходим из рекурсии
            if name_post_path != path_parts[path_index]:
                return None

            return check_parents(post_path_id, path_index + 1)

        def handle_double_dots(current_path):
            """обработка .. в пути"""
            nonlocal should_parents
            if path_parts and path_parts[0] == "..":
                # получаем ид родителя и удаляем .. из пути
                should_parents = FileManagerProxy.get_file_metadata(current_path)['parents'][0]
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
            list_id = FileManagerProxy.look_for_file(name=path_parts[0], mime_type="application/vnd.google-apps.folder")
        else:
            if mimeType:
                list_id = FileManagerProxy.look_for_file(name=path_parts[0], mime_type=mimeType)
            else:
                list_id = FileManagerProxy.look_for_file(name=path_parts[0])

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
            post_path = FileManagerProxy.get_file_metadata(parents_id)

            try:
                # Выделяем идентификатор родительской папки для род. папки
                post_path_id = post_path["parents"][0]
            except (KeyError, IndexError):
                return

            # Выделяем имя и записываем
            name_post_path = FileManagerProxy.look_for_file(file_id=parents_id)
            new_path.append(name_post_path)

            # Рекурсивно вызываем функцию для родительской папки
            check_parents(parents_id=post_path_id)

        check_parents(current_path_id)

        if new_path:
            # Обратный порядок, так как мы шли от текущей папки к корневой
            new_path.reverse()
            now_path = "/".join(new_path) + "/"
            # Соединяем элементы списка в строку
            os.environ["GOOGLE_CLOUD_CURRENT_ABSPATH_STR"] = now_path
            return "MyDrive/" + now_path
        else:
            os.environ["GOOGLE_CLOUD_CURRENT_ABSPATH_STR"] = ""
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
            start_path = PathNavigator.validate_path(path_parts, os.getenv("GOOGLE_CLOUD_CURRENT_PATH"))

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

        all_files = FileManagerProxy.get_list_of_files(called_directly=False)

        subfiles = []

        for file in all_files:
            if 'parents' in file and file['parents'][0] == source_id:
                if file['mimeType'] == 'application/vnd.google-apps.folder':
                    # ОЧень похоже на поиск в глубину (алгоритм DFS) !->?
                    subfiles = (subfiles + ["!"] + [file] +
                                PathNavigator.gather_structure(file['id']) + ["?"])
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
        all_files = FileManagerProxy.get_list_of_files(called_directly=False)
        list_child = []

        for file in all_files:
            if 'parents' in file and file['parents'][0] == source_id:
                list_child.append(file)

        return list_child

    @staticmethod
    def get_mime_description():
        """ Хранит в себе описания к mimeType, повторяет все из BiDict"""
        mime_info = [
            {"mime": "application/vnd.google-apps.document", "extension": ".gdoc",
             "description": "Google Docs document"},
            {"mime": "application/vnd.google-apps.spreadsheet", "extension": ".gsheet",
             "description": "Google Sheets spreadsheet"},
            {"mime": "application/vnd.google-apps.presentation", "extension": ".gslides",
             "description": "Google Slides presentation"},
            {"mime": "application/vnd.google-apps.form", "extension": ".gform", "description": "Google Forms form"},
            {"mime": "application/vnd.google-apps.drawing", "extension": ".gdraw",
             "description": "Google Drawings drawing"},
            {"mime": "application/vnd.google-apps.map", "extension": ".gmap", "description": "Google My Maps map"},
            {"mime": "application/vnd.google-apps.site", "extension": ".gsite", "description": "Google Sites site"},
            {"mime": "application/vnd.google-apps.script", "extension": ".gsheet", "description": "Google Apps Script"},
            {"mime": "application/vnd.google-apps.fusiontable", "extension": ".gtable",
             "description": "Google Fusion Tables table"},
            {"mime": "application/vnd.google-apps.jam", "extension": ".jam", "description": "Google Jamboard jam"},
            {"mime": "application/vnd.google-apps.shortcut", "extension": ".shortcut",
             "description": "Google Shortcuts shortcut"},
            {"mime": "application/vnd.google-apps.folder", "extension": "", "description": "Google Drive folder"},
            {"mime": "application/octet-stream", "extension": ".bin", "description": "Binary file"},
            {"mime": "text/plain", "extension": ".txt", "description": "Plain text file"},
            {"mime": "image/jpeg", "extension": ".jpeg", "description": "JPEG image file"},
            {"mime": "image/png", "extension": ".png", "description": "PNG image file"},
            {"mime": "image/gif", "extension": ".gif", "description": "GIF image file"},
            {"mime": "video/mp4", "extension": ".mp4", "description": "MP4 video file"},
            {"mime": "video/x-msvideo", "extension": ".avi", "description": "AVI video file"},
            {"mime": "audio/mpeg", "extension": ".mp3", "description": "MP3 audio file"},
            {"mime": "audio/x-wav", "extension": ".wav", "description": "WAV audio file"},
            {"mime": "application/pdf", "extension": ".pdf", "description": "PDF file"},
            {"mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "extension": ".docx",
             "description": "Microsoft Word document"},
            {"mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "extension": ".xlsx",
             "description": "Microsoft Excel spreadsheet"},
            {"mime": "application/vnd.openxmlformats-officedocument.presentationml.presentation", "extension": ".pptx",
             "description": "Microsoft PowerPoint presentation"},
            {"mime": "application/zip", "extension": ".zip", "description": "ZIP archive"}
        ]

        for reference in mime_info:
            UserInterface.show_message(
                f"{reference['mime']} ({reference['extension']}): {reference['description']}. "
            )
        return mime_info

    @staticmethod
    def refresh_completer(path):
        text = path.strip('"')
        text = text.strip("'")
        text = text.strip("/").split("/")

        _path = os.getenv('GOOGLE_CLOUD_CURRENT_ABSPATH_STR')

        def shnlex_path(path):
            if not ('/' in path):
                return ""
            index = path[:-1].rfind('/')
            return path[:index + 1]

        def handle_double_dots():
            nonlocal _path, text
            if text and text[0] == "..":
                if not _path:
                    nonlocal flag
                    flag = False
                    return
                # Найти позицию последнего вхождения символа "/"
                _path = shnlex_path(_path)
                text.pop(0)
                return handle_double_dots()

        flag = True

        handle_double_dots()

        if not flag:
            return None

        if text[0] == ".":
            # если требуется начать с нынешней директории
            text.pop(0)
            text[0] = _path + text[0]

        elif text[0] == "~":
            text.pop(0)
        else:
            text[0] = _path + text[0]

        path_ = "/".join(text)
        path = "~/" + path_

        for shtamp in PathNavigator.STRUCT:
            if path in shtamp:
                PathNavigator.STRUCT.remove(shtamp)

    @staticmethod
    def refresh_completer_trash(path):
        for shtamp in PathNavigator.STRUCT:
            if path in shtamp:
                PathNavigator.STRUCT.remove(shtamp)

    @staticmethod
    def prepare_completer(path="~/"):
        """
        Подгрузчик структуры для авто-дополнения.
        Огрзыок кода от команды tree
        Args:
            path (str) - путь от которого, строиться дерево
        """
        stop_loading = UserInterface.show_loading_message()

        source_id = PathNavigator.validate_path(path, os.getenv("GOOGLE_CLOUD_CURRENT_PATH"), check_file=True)

        if not source_id:
            UserInterface.show_error("Path is incorrect")
            stop_loading()
            return

        if path == "~/":
            indent = ""
            PathNavigator.STRUCT = []
        else:
            indent = PathNavigator.pwd(source_id)[8:]
            PathNavigator.STRUCT.append("~/" + indent[:-1])

        files = PathNavigator.gather_structure(source_id)

        iterator = iter(files)

        # использую стандартный итератор для фикса проблемы с извлечением следующего элемента при "?"
        for file in iterator:

            if file == "!":
                next_file = next(iterator, None)
                if not next_file:
                    break
                elif next_file == "?":
                    file = "?"
                else:
                    PathNavigator.STRUCT.append(f"~/{indent}{next_file['name']}/")
                    # улиняем путь так как поднялись на одну папку вверх
                    if next_file["mimeType"] == 'application/vnd.google-apps.folder':
                        indent = indent + next_file['name'] + "/"
                    continue

            if file == "?":
                # урезаем путь так как опустились на одну папку вверх
                indent = indent[:-1]
                i = len(indent) - 1
                while i >= 0 and indent[i] != "/":
                    indent = indent[:-1]
                    i -= 1

            if file != '!' and file != '?':
                PathNavigator.STRUCT.append(f"~/{indent}{file['name']}")
        stop_loading()

    @staticmethod
    def completer(text, state):
        """
        Комплитер для авто-дополнений
        """

        def get_last_argument(input_line):
            """
            Получает последний аргумент из строки ввода, учитывая возможные кавычки.
            """
            args = []
            in_quotes = False
            current_arg = ''
            for char in input_line:
                if char == '"':
                    in_quotes = not in_quotes
                if char == "'":
                    in_quotes = not in_quotes
                elif char == ' ' and not in_quotes:
                    if current_arg:
                        args.append(current_arg)
                        current_arg = ''
                else:
                    current_arg += char
            if current_arg:
                args.append(current_arg)

            # Последний аргумент
            if args:
                last_arg = args[-1]
            else:
                last_arg = ''

            # Убираем кавычки, если они есть
            last_arg = last_arg.strip('"').strip("'")

            return last_arg

        # Получаем всю строку ввода
        input_line = readline.get_line_buffer()

        last_arg = get_last_argument(input_line)
        text = last_arg

        text = re.sub('\n', "", text)

        text = text.strip('"')
        text = text.strip("'")
        text = text.strip("/").split("/")

        _path = os.getenv('GOOGLE_CLOUD_CURRENT_ABSPATH_STR')

        def shnlex_path(path):
            if not ('/' in path):
                return ""
            index = path[:-1].rfind('/')
            return path[:index + 1]

        def handle_double_dots():
            nonlocal _path, text
            if text and text[0] == "..":
                if not _path:
                    nonlocal flag
                    flag = False
                    return
                # Найти позицию последнего вхождения символа "/"
                _path = shnlex_path(_path)
                text.pop(0)
                return handle_double_dots()

        flag = True

        handle_double_dots()

        if not flag:
            return None

        if text[0] == ".":
            # если требуется начать с нынешней директории
            text.pop(0)
            text[0] = _path + text[0]

        elif text[0] == "~":
            text.pop(0)
        else:
            text[0] = _path + text[0]

        path_ = "/".join(text)
        path = "~/" + path_

        # Пример автодополнения: смотрим в STRUCT и предлагаем совпадения
        options = [
            entry for entry in PathNavigator.STRUCT
            if entry.startswith(path) and path != entry.rstrip("/") and
            entry.count('/') <= path.count('/') + 1 and
            (entry.count('/') != path.count('/') + 1 or not entry[entry.rfind('/') + 1:])
        ]

        if last_arg[-1] == "/" and len(options) != 1:
            return None

        # Если есть только один вариант, автоматически дополняем его
        if state < len(options):
            option_to_insert = options[state][2:]
            # РЕПЛАЙСЕ НЕ РАБОАТЕТ, Я ТАК И НЕ ПОНЯЛ ПОЧЕМУ
            #option_to_insert = option_to_insert.replace(path, "",1)
            path_list = list(path[2:])
            option_list = list(option_to_insert)

            for char in path_list:
                if option_list and char == option_list[0]:
                    option_list.pop(0)
                else:
                    break
            path = path[path.rfind("/")+1:]
            final_option = ''.join(option_list)
            if " " in path:
                path = path.split()
                return path[-1] + final_option
            else:
                return path + final_option
        else:
            return None
