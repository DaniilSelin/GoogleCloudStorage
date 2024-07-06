import sys
import time
import threading


class UserInterface:
    """"
    Класс для"оповещений" пользователя.

    Принимаемый формат: [{<ключ сообщения>:<занчение ключа>,...},...]
    Возможные ключи для форматирования:
    text: Строка текста.
    color: Цвет текста.
    style: Стиль текста, например:
        "bold": Жирный текст.
        "italic": Курсив.
        "underline": Подчеркнутый текст.
    clear: Очищать ли строку перед выводом, базово стоит Ture,
            Если очищать не надо: <clear>:""
            Если нужно использовать другой спец-символ: <clear>:"<спец-символ>"
    """

    COLORS = {
        'reset': "\033[0m",
        'black': "\033[30m",
        'red': "\033[31m",
        'green': "\033[32m",
        'yellow': "\033[33m",
        'blue': "\033[34m",
        'magenta': "\033[35m",
        'cyan': "\033[36m",
        'white': "\033[37m",
        'bright_black': "\033[90m",
        'bright_red': "\033[91m",
        'bright_green': "\033[92m",
        'bright_yellow': "\033[93m",
        'bright_blue': "\033[94m",
        'bright_magenta': "\033[95m",
        'bright_cyan': "\033[96m",
        'bright_white': "\033[97m"
    }

    STYLES = {
        'bold': "\033[1m",
        'italic': "\033[3m",
        'underline': "\033[4m"
    }

    @staticmethod
    def show_loading_message(completion_message=None):
        global stop_loading
        animation = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        idx = 0
        # утсанавеваем событие для завершения анимации
        stop_loading = threading.Event()

        def loading():
            nonlocal idx
            while not stop_loading.is_set():
                sys.stdout.write(f"\rLoading {animation[idx % len(animation)]}")
                sys.stdout.flush()
                idx += 1
                time.sleep(0.16)
            sys.stdout.write("\r" + " " * 20 + "\r")  # Очищаем строку после остановки
            if completion_message:
                formatted_message = UserInterface.format_message(completion_message) if isinstance(completion_message, list) else completion_message
                sys.stdout.write(formatted_message + '\n')
            sys.stdout.flush()

        t = threading.Thread(target=loading)
        t.start()

        def stop():
            stop_loading.set()
            t.join()  # Дожидаемся завершения потока

        return stop

    @staticmethod
    def stop_loading_animation():
        """ Для экстренной остановки анимации """
        if stop_loading:
            stop_loading.set()

    @staticmethod
    def format_message(segments):
        formatted_message = ""
        for segment in segments:
            text = segment.get('text', '')
            color = UserInterface.COLORS.get(segment.get('color', 'reset'), '')
            style = UserInterface.STYLES.get(segment.get('style', ''), '')
            clear = segment.get("clear", "\r")
            formatted_message += f"{clear}{color}{style}{text}{UserInterface.COLORS['reset']}"
        return formatted_message

    @staticmethod
    def show_message(message, end="\n"):
        if isinstance(message, list):
            formatted_message = UserInterface.format_message(message)
        else:
            formatted_message = "\r" + message
        sys.stdout.write(formatted_message + end)

    @staticmethod
    def show_error(error_message):
        if isinstance(error_message, list):
            formatted_message = UserInterface.format_message(error_message)
        else:
            formatted_message = "\r" + error_message
        sys.stdout.write("\r" + UserInterface.COLORS['red'] + formatted_message + UserInterface.COLORS['reset'] + '\n')

    @staticmethod
    def show_success(success_message):
        if isinstance(success_message, list):
            formatted_message = UserInterface.format_message(success_message)
        else:
            formatted_message = "\r" + success_message
        sys.stdout.write(UserInterface.COLORS['green'] + formatted_message + UserInterface.COLORS['reset'] + '\n')


# Создание сокращения внутри класса
UI = UserInterface

# Пример использования
if __name__ == "__main__":
    UI = UserInterface

    UI.show_message([{'text': 'Starting authorization process...', 'color': 'bright_yellow'}])
    UI.show_success([{'text': 'Authorization successful.', 'color': 'green'}])
    UI.show_error([{'text': 'Failed to retrieve user drive ID. ', 'color': 'red'}, {'text': 'Please reauthorize.', 'color': 'yellow'}])
    stop_loading = UserInterface.show_loading_message("Loading complete!")
    time.sleep(5)  # Симулируем процесс
    stop_loading()