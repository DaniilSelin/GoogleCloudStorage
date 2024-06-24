import json
import unittest
import sys
import json
import subprocess
import load_to_cloud


with open('test_struct.json', 'r') as file:
    test_cases = json.load(file)


class Testing(unittest.TestCase):
    terminal = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # контейнер для мусора
        self.garbage = []
        #создаем терминал для наших тестов
        self.terminal = load_to_cloud.GoogleCloudTerminal(
            token_path="../token.json",
            credentials_path="../credentials.json"
        )

    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        # Инициализируем экземпляр GoogleCloudTerminal, если он еще не был инициализирован
        if cls.terminal is None:
            cls.terminal = load_to_cloud.GoogleCloudTerminal(
                token_path="../token.json",
                credentials_path="../credentials.json"
            )

        cls.test_cases = test_cases

        # Здесь запускаем создание тестируемой структуры чере mkdir
        test_cases_cd = test_cases['mkdir']

        for tester in test_cases_cd:
            sys.stdout.write(f'\n{load_to_cloud.PathNavigator.pwd(cls.terminal.current_path)} $ {tester}\n')
            cls.terminal.execute_command(tester)

    @classmethod
    def tearDownClass(cls):
        # чситим дериктории которые намутили
        test_cases_cd = test_cases['rm']

        for tester in test_cases_cd:
            sys.stdout.write(f'\n{load_to_cloud.PathNavigator.pwd(cls.terminal.current_path)} $ {tester}\n')
            cls.terminal.execute_command(tester)

    def test_cd(self):
        test_cases_cd = test_cases['cd']

        for tester in test_cases_cd:
            sys.stdout.write(f'\n{load_to_cloud.PathNavigator.pwd(self.terminal.current_path)} $ {tester}\n')
            self.terminal.execute_command(tester)

    def test_ls(self):
        test_cases_cd = test_cases['ls']

        for tester in test_cases_cd:
            sys.stdout.write(f'\n{load_to_cloud.PathNavigator.pwd(self.terminal.current_path)} $ {tester}\n')
            self.terminal.execute_command(tester)


if __name__ == '__main__':
    unittest.main()


