import os
import os.path
from typing import Dict, Optional

import yaml
from pydantic import BaseModel, Field

from pyobas.configuration.sources import DictionarySource, EnvironmentSource
from pyobas.exceptions import ConfigurationError

CONFIGURATION_TYPES = str | int | bool | None


def is_truthy(value: str) -> bool:
    return value.lower() in ["yes", "true"]


def is_falsy(value: str) -> bool:
    return value.lower() in ["no", "false"]


class ConfigurationHint(BaseModel):
    data: Optional[str] = Field(default=None)
    env: Optional[str] = Field(default=None)
    file_path: Optional[list[str]] = Field(default=None)
    is_number: Optional[bool] = Field(default=False)
    default: Optional[CONFIGURATION_TYPES] = Field(default=None)


class Configuration:
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
        config = self.__config_hints.get(config_key)
        if config is None:
            return None

        return self.__process_value_to_type(
            config.data or self.__dig_config_sources_for_key(config), config.is_number
        )

    def set(self, config_key: str, value: CONFIGURATION_TYPES):
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
