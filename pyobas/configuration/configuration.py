import os
import os.path
import yaml
from typing import Dict, Optional
from pydantic import BaseModel, Field
from pyobas.exceptions import ConfigurationError
from pyobas.configuration.sources import EnvironmentSource, DictionarySource

CONFIGURATION_TYPES = str | int | bool |  None

def is_truthy(value: str) -> bool:
    return value.lower() in ["yes", "true"]


def is_falsy(value: str) -> bool:
    return value.lower() in ["no", "false"]


class ConfigurationKey(BaseModel):
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
            config_file_path: str = os.path.join(os.curdir, "config.yml")
    ):
        self.__config_hints = {
            key: (
                ConfigurationKey(**value)
                if isinstance(value, dict)
                else ConfigurationKey(**{"default": value})
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
            raise ConfigurationError(f"Could not find configuration key: {config_key}")

        return config.data or self.__dig_config_sources_for_key(config)

    def __dig_config_sources_for_key(
        self, config: ConfigurationKey
    ) -> CONFIGURATION_TYPES:
        result = (
            EnvironmentSource.get(config.env)
            or DictionarySource.get(config.file_path, self.__config_values)
        )
        if result is None:
            return config.default

        if isinstance(result, int) or config.is_number:
            return int(result)
        if is_truthy(result):
            return True
        if is_falsy(result):
            return False

        if isinstance(result, str) and len(result) == 0:
            return config.default

        return result
