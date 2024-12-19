import os
import unittest
from unittest.mock import patch

from pyobas.configuration import Configuration

TEST_CONFIG_HINTS = {
    "string_config_direct": {"data": "this is string_config_direct"},
    "string_config_no_default": {
        "env": "PYOBAS_TEST_CONFIGURATION_STRING_CONFIG_NO_DEFAULT",
        "file_path": ["pyobas_test_configuration", "string_config_no_default"],
    },
    "int_config_no_default": {
        "env": "PYOBAS_TEST_CONFIGURATION_INT_CONFIG_NO_DEFAULT",
        "file_path": ["pyobas_test_configuration", "int_config_no_default"],
        "is_number": True,
    },
    "int_config_no_default_not_marked_number": {
        "env": "PYOBAS_TEST_CONFIGURATION_INT_CONFIG_NO_DEFAULT",
        "file_path": [
            "pyobas_test_configuration",
            "int_config_no_default_not_marked_number",
        ],
    },
    "string_config_with_default": {
        "env": "PYOBAS_TEST_CONFIGURATION_STRING_CONFIG_WITH_DEFAULT",
        "file_path": ["pyobas_test_configuration", "string_config_with_default"],
        "default": "default string config",
    },
    "int_config_with_default": {
        "env": "PYOBAS_TEST_CONFIGURATION_INT_CONFIG_WITH_DEFAULT",
        "file_path": ["pyobas_test_configuration", "int_config_with_default"],
        "is_number": True,
        "default": 777_777,
    },
    "bool_config_with_default": {
        "env": "PYOBAS_TEST_CONFIGURATION_BOOL_CONFIG_WITH_DEFAULT",
        "file_path": ["pyobas_test_configuration", "bool_config_with_default"],
        "default": True,
    },
}


class TestConfiguration(unittest.TestCase):
    def test_when_string_config_has_no_default_when_key_not_found_return_None(self):
        config_obj = Configuration(
            config_hints=TEST_CONFIG_HINTS,
        )

        value = config_obj.get("string_config_no_default")

        self.assertIsNone(value)

    def test_when_config_has_no_default_when_key_is_set_as_bool_return_bool(self):
        config_obj = Configuration(
            config_hints=TEST_CONFIG_HINTS,
        )
        config_obj.set("string_config_no_default", True)

        value = config_obj.get("string_config_no_default")

        self.assertEqual(value, True)

    def test_when_config_has_no_default_when_key_is_set_as_string_bool_return_bool(
        self,
    ):
        config_obj = Configuration(
            config_hints=TEST_CONFIG_HINTS,
        )
        config_obj.set("string_config_no_default", "yes")

        value = config_obj.get("string_config_no_default")

        self.assertEqual(value, True)

    def test_when_string_config_has_default_when_key_not_found_return_default(self):
        config_obj = Configuration(
            config_hints=TEST_CONFIG_HINTS,
        )

        value = config_obj.get("string_config_with_default")

        self.assertEqual(value, "default string config")

    @patch.dict(
        os.environ,
        values={"PYOBAS_TEST_CONFIGURATION_STRING_CONFIG_NO_DEFAULT": "actual value"},
        clear=True,
    )
    def test_when_string_config_has_no_default_when_key_is_in_env_return_env_value(
        self,
    ):
        config_obj = Configuration(
            config_hints=TEST_CONFIG_HINTS,
        )

        value = config_obj.get("string_config_no_default")

        self.assertEqual(value, "actual value")

    @patch.dict(
        os.environ,
        values={"PYOBAS_TEST_CONFIGURATION_STRING_CONFIG_WITH_DEFAULT": "actual value"},
        clear=True,
    )
    def test_when_string_config_has_default_when_key_is_in_env_return_env_value(self):
        config_obj = Configuration(
            config_hints=TEST_CONFIG_HINTS,
        )

        value = config_obj.get("string_config_with_default")

        self.assertEqual(value, "actual value")

    @patch.dict(
        os.environ,
        values={"PYOBAS_TEST_CONFIGURATION_STRING_CONFIG_NO_DEFAULT": "actual value"},
        clear=True,
    )
    def test_when_key_is_in_both_env_and_file_return_env_value(self):
        config_obj = Configuration(
            config_hints=TEST_CONFIG_HINTS,
            config_values={
                "pyobas_test_configuration": {
                    "string_config_no_default": "another value"
                }
            },
        )

        value = config_obj.get("string_config_no_default")

        self.assertEqual(value, "actual value")

    @patch.dict(
        os.environ,
        values={"PYOBAS_TEST_CONFIGURATION_STRING_CONFIG_NO_DEFAULT": "env value"},
        clear=True,
    )
    def test_when_key_is_in_both_env_and_file_when_value_is_set_return_set_value(self):
        config_obj = Configuration(
            config_hints=TEST_CONFIG_HINTS,
            config_values={
                "pyobas_test_configuration": {"string_config_no_default": "file value"}
            },
        )
        config_obj.set("string_config_no_default", "set value")

        value = config_obj.get("string_config_no_default")

        self.assertEqual(value, "set value")

    def test_when_string_config_has_no_default_when_key_is_in_file_return_file_value(
        self,
    ):
        config_obj = Configuration(
            config_hints=TEST_CONFIG_HINTS,
            config_values={
                "pyobas_test_configuration": {
                    "string_config_no_default": "another value"
                }
            },
        )

        value = config_obj.get("string_config_no_default")

        self.assertEqual(value, "another value")

    def test_when_int_config_has_no_default_when_key_is_not_found_return_None(self):
        config_obj = Configuration(
            config_hints=TEST_CONFIG_HINTS,
        )

        value = config_obj.get("int_config_no_default")

        self.assertIsNone(value)

    def test_when_int_config_has_default_when_key_is_not_found_return_default(self):
        config_obj = Configuration(
            config_hints=TEST_CONFIG_HINTS,
        )

        value = config_obj.get("int_config_with_default")

        self.assertEqual(value, 777_777)

    @patch.dict(
        os.environ,
        values={"PYOBAS_TEST_CONFIGURATION_INT_CONFIG_NO_DEFAULT": "1234"},
        clear=True,
    )
    def test_when_int_config_has_no_default_when_key_is_in_env_return_env_value(self):
        config_obj = Configuration(
            config_hints=TEST_CONFIG_HINTS,
        )

        value = config_obj.get("int_config_no_default")

        self.assertEqual(value, 1234)

    def test_when_int_config_has_no_default_when_key_is_passed_as_int_return_int_value(
        self,
    ):
        config_obj = Configuration(
            config_hints=TEST_CONFIG_HINTS,
            config_values={
                "pyobas_test_configuration": {"int_config_no_default": 456_123}
            },
        )

        value = config_obj.get("int_config_no_default")

        self.assertEqual(value, 456_123)

    def test_when_int_config_has_no_default_when_key_is_passed_as_int_when_config_is_not_marked_as_number_return_int_value(
        self,
    ):
        config_obj = Configuration(
            config_hints=TEST_CONFIG_HINTS,
            config_values={
                "pyobas_test_configuration": {
                    "int_config_no_default_not_marked_number": 842_204
                }
            },
        )

        value = config_obj.get("int_config_no_default_not_marked_number")

        self.assertEqual(value, 842_204)

    @patch.dict(
        os.environ,
        values={"PYOBAS_TEST_CONFIGURATION_STRING_CONFIG_NO_DEFAULT": "yes"},
        clear=True,
    )
    def test_when_string_config_has_no_default_when_string_is_boolean_when_key_is_in_env_return_env_value(
        self,
    ):
        config_obj = Configuration(
            config_hints=TEST_CONFIG_HINTS,
        )

        value = config_obj.get("string_config_no_default")

        self.assertEqual(value, True)

    def test_when_bool_config_has_default_when_key_is_not_found_return_default(self):
        config_obj = Configuration(
            config_hints=TEST_CONFIG_HINTS,
        )

        value = config_obj.get("bool_config_with_default")

        self.assertEqual(value, True)


if __name__ == "__main__":
    unittest.main()
