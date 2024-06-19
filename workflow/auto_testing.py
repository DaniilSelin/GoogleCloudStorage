import json
import unittest
#так как могут потребоваться фикстуры для регистрации в Gooogle API
import pytest
import json
import subprocess
import load_to_cloud

def input_recomande(input_set: list) -> str:
    return input_set

with open('test_struct.json', 'r') as file:
    test_cases = json.load(file)

name_test_file = "../load_to_cloud.py"

"""
class Testing(unittest.TestCase):
    def setUp(self):
        self.test_cases = test_cases

    def testing(self):
        for input_set in self.test_cases:
            input_value = input_recomande(input_set["input"])
            expected_output = input_set["expected_output"]

            with self.subTest(input_valuse=input_value):
                result = subprocess.run(
                    ['/usr/bin/python3', name_test_file],
                    input=input_value,
                    capture_output=True,
                    text=True,
                )
                output = result.stdout.strip()
                self.assertEqual(output, expected_output)"""

if __name__ == '__main__':
    with open('test_struct.json', 'r') as file:
        test_cases = json.load(file)
    file_tester = list(test_cases.items())[0]
    _key,_ = file_tester
    print(f'File tester: {_["name"]}', " ", f'ID: {_["id"]}')
    del test_cases[_key]
    creds = load_to_cloud.authorization(token_path="../token.json", credentials_path="../credentials.json")
    files_involved =[]
    for number_test, (key, value) in enumerate(test_cases.items(), start=1):
        print(f'Path {number_test}: {value["path_parts"]}', " ", f'ID: {value["id"]}')
        file = load_to_cloud.copy(creds,file_id=_["id"], path=value["path_parts"])
        files_involved.append(file['id'])
        print("\n")

    print("")

    for file_id in files_involved:
        load_to_cloud.remove(creds, file_id)


