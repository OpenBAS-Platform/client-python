import os


class EnvironmentSource:
    @classmethod
    def get(cls, config_key: str) -> str:
        return os.getenv(config_key)

class DictionarySource:
    # this is quite hacky
    # it only strictly handles two levels of keys in a dict
    @classmethod
    def get(cls, config_key_path: list[str], source_dict: dict) -> str:
        assert isinstance(config_key_path, list) and len(config_key_path) == 2 and all([len(path_part) > 0 for path_part in config_key_path])
        return source_dict.get(
            config_key_path[0], {config_key_path[1]: None}
        ).get(config_key_path[1])