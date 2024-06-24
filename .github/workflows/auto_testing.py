import json
import unittest
import load_to_cloud
import os

import os

# ест ли у нас директория для логов?
if not os.path.exists('test-reports'):
    os.makedirs('test-reports')

# есть ли там файл?
results_file = 'test-reports/results.log'
if not os.path.exists(results_file):
    with open(results_file, 'w'):
        pass  # Создание пустого файла

# Определяем абсолютный путь к текущему файлу
current_dir = os.path.dirname(os.path.abspath(__file__))
# получаем тест кейсы
with open(os.path.join(current_dir, "test_struct.json"), "r") as test_struct:
    test_cases = json.load(test_struct)

class Testing(unittest.TestCase):
    terminal = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #создаем терминал для наших тестов
        self.terminal = load_to_cloud.GoogleCloudTerminal(
            token_path=os.path.join(os.path.dirname(__file__), "../../token.json"),
            credentials_path=os.path.join(os.path.dirname(__file__), "../../credentials.json")
        )

    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        # Инициализируем экземпляр GoogleCloudTerminal, если он еще не был инициализирован
        if cls.terminal is None:
            cls.terminal = load_to_cloud.GoogleCloudTerminal(
                token_path=os.path.join(os.path.dirname(__file__), "../../token.json"),
                credentials_path=os.path.join(os.path.dirname(__file__), "../../credentials.json")
            )

        cls.test_cases = test_cases

        # Здесь запускаем создание тестируемой структуры через mkdir
        test_cases_cd = test_cases['mkdir']

        for tester in test_cases_cd:
            print(f'\n{load_to_cloud.PathNavigator.pwd(cls.terminal.current_path)} $ {tester}')
            cls.terminal.execute_command(tester)

    @classmethod
    def tearDownClass(cls):
        # чистим директории которые создали
        test_cases_cd = test_cases['rm']

        for tester in test_cases_cd:
            print(f'\n{load_to_cloud.PathNavigator.pwd(cls.terminal.current_path)} $ {tester}')
            cls.terminal.execute_command(tester)

    def test_cd(self):
        test_cases_cd = test_cases['cd']

        for tester in test_cases_cd:
            print(f'\n{load_to_cloud.PathNavigator.pwd(self.terminal.current_path)} $ {tester}')
            self.terminal.execute_command(tester)

    def test_ls(self):
        test_cases_cd = test_cases['ls']

        for tester in test_cases_cd:
            print(f'\n{load_to_cloud.PathNavigator.pwd(self.terminal.current_path)} $ {tester}')
            self.terminal.execute_command(tester)


if __name__ == '__main__':
    unittest.main()
