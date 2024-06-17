import json
import unittest

import unittest
import json
import subprocess

def input_recomande(input_set: list) -> str:

    return input_set

with open('test_struct.json', 'r') as file:
    test_cases = json.load(file)

name_test_file = "../load_to_cloud.py"

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
                self.assertEqual(output, expected_output)

if __name__ == '__main__':
    unittest.main()