import os


class EnvironmentSource:
    """A utility for fecthing a value in the env vars."""

    @classmethod
    def get(cls, env_var: str) -> str | None:
        """Gets the value for the specified env var

        :param env_var: the name of the env var to query
        :type env_var: str

        :return: value of the env var, or None if not found
        :rtype: str | None
        """
        return os.getenv(env_var)


class DictionarySource:
    """A utility for fetching a value from within a JSON-like (nested dict) structure"""

    # this is quite hacky
    # it only strictly handles two levels of keys in a dict
    @classmethod
    def get(cls, config_key_path: list[str], source_dict: dict) -> str | None:
        """Gets the value for the specified env var

        :param config_key_path: the two-level dictionary path to the config key
        :type config_key_path: list[str]
        :param source_dict: JSON-like (nested dict) structure containing config values.
        :type source_dict: dict

        :return: value for the config key at specified path, or None if not found
        :rtype: str | None
        """
        assert (
            isinstance(config_key_path, list)
            and len(config_key_path) == 2
            and all([len(path_part) > 0 for path_part in config_key_path])
        )
        return source_dict.get(config_key_path[0], {config_key_path[1]: None}).get(
            config_key_path[1]
        )
