import os
import unittest
from unittest.mock import patch

from pyobas.configuration.sources import DictionarySource, EnvironmentSource

TEST_ENV_VAR: str = "PYOBAS_TEST_ENV_VAR"


class TestEnvironmentSource(unittest.TestCase):
    @patch.dict(os.environ, clear=True)
    def test_when_env_var_not_set_return_none(self):
        result = EnvironmentSource.get(TEST_ENV_VAR)

        self.assertIsNone(result)

    @patch.dict(os.environ, values={TEST_ENV_VAR: "some_value"}, clear=True)
    def test_when_env_var_is_set_return_value(self):
        result = EnvironmentSource.get(TEST_ENV_VAR)

        self.assertEqual(result, "some_value")


class TestDictionarySource(unittest.TestCase):
    def test_when_config_key_path_is_not_list_it_throws(self):
        string_key_path = "some string"
        with self.assertRaises(AssertionError):
            DictionarySource.get(string_key_path, {})

    def test_when_config_key_path_has_not_2_elements_it_throws(self):
        key_path = ["element 1"]
        with self.assertRaises(AssertionError):
            DictionarySource.get(key_path, {})

    def test_when_config_key_path_has_empty_elements_it_throws(self):
        key_path = ["element 1", ""]
        with self.assertRaises(AssertionError):
            DictionarySource.get(key_path, {})

    def test_when_config_missing_first_path_part_return_None(self):
        expected_value = None
        key_path = ["element 1", "element 2"]
        values = {"not element 1": None}

        result = DictionarySource.get(key_path, values)

        self.assertEqual(result, expected_value)

    def test_when_config_missing_second_path_part_return_None(self):
        expected_value = None
        key_path = ["element 1", "element 2"]
        values = {"element 1": {"not element 2": "some value"}}

        result = DictionarySource.get(key_path, values)

        self.assertEqual(result, expected_value)

    def test_when_config_found_return_value(self):
        expected_value = "expected!"
        key_path = ["element 1", "element 2"]
        values = {"element 1": {"element 2": expected_value}}

        result = DictionarySource.get(key_path, values)

        self.assertEqual(result, expected_value)


if __name__ == "__main__":
    unittest.main()
