import os
import os.path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field

from pyobas.configuration.sources import DictionarySource, EnvironmentSource

CONFIGURATION_TYPES = str | int | bool | Any | None


def is_truthy(value: str) -> bool:
    """Asserts whether a given string signals a "True" value

    :param value: value to test
    :type value: str

    :return: whether the string represents True or not.
    :rtype: bool
    """
    return value.lower() in ["yes", "true"]


def is_falsy(value: str) -> bool:
    """Asserts whether a given string signals a "False" value

    :param value: value to test
    :type value: str

    :return: whether the string represents False or not.
    :rtype: bool
    """
    return value.lower() in ["no", "false"]


class ConfigurationHint(BaseModel):
    """An individual configuration hint. This allows for specifying
    where any given configuration key can be found, in env vars,
    config files. Additionally, it may define a default value or
    a discrete override value.
    """

    data: Optional[CONFIGURATION_TYPES] = Field(default=None)
    """Override value; when set, getting the configuration value for
        the key described in this instance returns this value.
    """
    env: Optional[str] = Field(default=None)
    """Defines which env var should be read for getting the value
    """
    file_path: Optional[list[str]] = Field(default=None)
    """Defines a JSON path (nested keys) to follow in the provided
        config file for reaching the value.
        
        Example: ["toplevel", "subkey"] will hint for searching for 
        the config key at { "toplevel": { "subkey": { "config_key"}}
    """
    is_number: Optional[bool] = Field(default=False)
    """Hints at whteher the configuration value should be
        interpreted as a number.
    """
    default: Optional[CONFIGURATION_TYPES] = Field(default=None)
    """When defined, provides a default value for whenever none of the
        hinted locations or the data field have a value.
    """


class Configuration:
    """A configuration object providing ways to an interface for getting
    configuration values. It should be provided with a collection of hints
    to enable its behaviour.

        :param config_hints: a dictionary of hints, for which the key is the
            desired configuration key (e.g. "log_level") and the value is either
            a dictionary of hints (see ConfigurationHint) or a standalone string.
            In the latter case, the string will be interpreted as a default value.

            Example:
            .. code-block:: python
                {
                    "my_config_key": {
                        "env" : "MY_CONFIG_VALUE_ENV_VAR",
                        "file_path": ["first_level", "second_level"]
                    },
                    "my_other_config_key: "discrete value"
                }
        :type config_hints: Dict[str, dict | str]
        :param config_values: dictionary of config values to preemptively load into the
            Configuration object. The format of this dictionary should follow the patterns
            chosen in the file_path property of ConfigurationHint object passed
            as config_hints, defaults to None

            Example:
            .. code-block:: python
                {
                    "first_level": {
                        "second_level": {
                            "my_config_key": "some value"
                        }
                    }
                }
        :type config_values: dict (json), optional
        :param config_file_path: path to the configuration file. The file should
            contain a json structure that matches the format of the config_values param,
            defaults to './config.yml' (relative path).
        :type config_file_path: str
    """

    def __init__(
        self,
        config_hints: Dict[str, dict | str],
        config_values: dict = None,
        config_file_path: str = os.path.join(os.curdir, "config.yml"),
    ):
        self.__config_hints = {
            key: (
                ConfigurationHint(**value)
                if isinstance(value, dict)
                else ConfigurationHint(**{"default": value})
            )
            for key, value in config_hints.items()
        }

        file_contents = (
            yaml.load(open(config_file_path), Loader=yaml.FullLoader)
            if os.path.isfile(config_file_path)
            else {}
        )

        self.__config_values = (config_values or {}) | file_contents

    def get(self, config_key: str) -> CONFIGURATION_TYPES:
        """Gets the value pointed to by the configuration key. If the key is defined
        with actual hints (as opposed to a discrete value), it will use those hints to
        potentially find a value. If the key was not defined as part of the supplied
        config_hints, this will always return None.

        :param config_key: the configuration key to search a value for.
        :type config_key: str

        :return: the value pointed to by the configuration key, or None if not found
        :rtype: CONFIGURATION_TYPES
        """
        config = self.__config_hints.get(config_key)
        if config is None:
            return None

        return self.__process_value_to_type(
            config.data or self.__dig_config_sources_for_key(config), config.is_number
        )

    def set(self, config_key: str, value: CONFIGURATION_TYPES):
        """Sets an arbitrary value in the Configuration object, for
        the supplied configuration key, after which any request for the value
        of that key will return this new value.

        :param config_key: the configuration key to set a value for.
        :type config_key: str
        :param value: the new value to set for the configuration key.
        :type value: CONFIGURATION_TYPES
        """
        if config_key not in self.__config_hints:
            self.__config_hints[config_key] = ConfigurationHint(**{"data": value})
        else:
            self.__config_hints[config_key].data = value

    @staticmethod
    def __process_value_to_type(value: CONFIGURATION_TYPES, is_number_hint: bool):
        if value is None:
            return value
        if isinstance(value, int) or is_number_hint:
            return int(value)
        if isinstance(value, str):
            if is_truthy(value):
                return True
            if is_falsy(value):
                return False
            if len(value) == 0:
                return None
        return value

    def __dig_config_sources_for_key(
        self, config: ConfigurationHint
    ) -> CONFIGURATION_TYPES:
        result = EnvironmentSource.get(config.env) or DictionarySource.get(
            config.file_path, self.__config_values
        )
        return result or config.default
