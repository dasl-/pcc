import os
import pyjson5
from pcc.logger import Logger
from pcc.directoryutils import DirectoryUtils

class Config:

    __CONFIG_PATH = DirectoryUtils().root_dir + '/config.json'
    __DEFAULT_CONFIG_PATH = DirectoryUtils().root_dir + '/default_config.json'

    __is_loaded = False
    __config = {}
    __logger = Logger().set_namespace('Config')
    __PATH_SEP = '.'

    # Get a key from config using dot notation: "foo.bar.baz"
    @staticmethod
    def get(key, default = None):
        return Config.__get(key, should_throw = False, default = default)

    @staticmethod
    def get_or_throw(key):
        return Config.__get(key, should_throw = True, default = None)

    @staticmethod
    def set(key, value):
        Config.load_config_if_not_loaded()

        new_config = Config.__set_nested(key.split(Config.__PATH_SEP), value, Config.__config)
        Config.__config = new_config

    """
    Merges the config located at __DEFAULT_CONFIG_PATH with the config located at __CONFIG_PATH.
    Example:

    Config located at __DEFAULT_CONFIG_PATH:
    {
        "foo": {
            "bam": {
                "ba": "ba",
                "booyah": "booyah"
            },
            "bar": "bar",
            "baz": "baz",
            "boo": {
                "yo": "yo"
            },
            "boop": "boop"
        }
    }

    Config located at __CONFIG_PATH:
    {
        "foo": {
            "bam": {
                "ba": "ba_override",
                "bb": "bb"
            },
            "baz": "baz_override",
            "bing": "bing",
            "boo": {}
        }
    }

    Merged config:
    {
        "foo": {
            "bam": {
                "ba": "ba_override",
                "bb": "bb",
                "booyah": "booyah"
            },
            "bar": "bar",
            "baz": "baz_override",
            "bing": "bing",
            "boo": {},
            "boop": "boop"
        }
    }
    """
    @staticmethod
    def load_config_if_not_loaded(should_set_log_level = True):
        if Config.__is_loaded:
            return

        if os.path.exists(Config.__DEFAULT_CONFIG_PATH):
            Config.__logger.info(f"Found config file at: {Config.__DEFAULT_CONFIG_PATH}.")
        else:
            raise Exception(f"No config file found at: {Config.__DEFAULT_CONFIG_PATH}.")

        if os.path.exists(Config.__CONFIG_PATH):
            Config.__logger.info(f"Found config file at: {Config.__CONFIG_PATH}.")
        else:
            Config.__logger.info(f"No config file found at: {Config.__CONFIG_PATH}.")

        with open(Config.__DEFAULT_CONFIG_PATH) as default_config_json:
            Config.__config = pyjson5.decode(default_config_json.read())

        with open(Config.__CONFIG_PATH) as config_json:
            overrides = pyjson5.decode(config_json.read())

            key_stack = []
            for key in overrides.keys():
                key_stack.append([key])

            for key in key_stack:
                value = Config.__get(key, True, None, overrides)
                if isinstance(value, dict) and value:
                    for nested_key in value.keys():
                        new_key = key.copy()
                        new_key.append(nested_key)
                        key_stack.append(new_key)
                else:
                    Config.__set_nested(key, value, Config.__config)

            if 'log_level' in Config.__config and should_set_log_level:
                Logger.set_level(Config.__config['log_level'])

        Config.__is_loaded = True

    # Returns the value of `key` from `config`.
    # `key`: may be expressed be in dot notation, e.g. "foo.bar.baz"
    #        may also be expressed in array notation, e.g. ["foo", "bar", "baz""]
    #        Both would return a nested key from e.g. {"foo": {"bar": {"baz": 123}}}
    # `config`: if not specified, return the key from the global config dictionary.
    @staticmethod
    def __get(key, should_throw = False, default = None, config = None):
        if config is None:
            Config.load_config_if_not_loaded()
            config = Config.__config

        if isinstance(key, str):
            keys = key.split(Config.__PATH_SEP)
        else:
            keys = key

        for key in keys:
            if key in config:
                config = config[key]
            else:
                if should_throw:
                    raise KeyError(f"{key}")
                else:
                    return default
        return config

    """
    keys: list of string keys
    value: any value
    my_dict: a dict in which to set the nested list of keys to the given value

    returns: a dict identical to my_dict, except with the nested dict element identified
        by the list of keys set to the given value

    Ex:
        >>> __set_nested(['foo'], 1, {})
        {'foo': 1}

        >>> __set_nested(['foo', 'bar'], 1, {})
        {'foo': {'bar': 1}}

        >>> __set_nested(['foo'], 1, {'foo': 2})
        {'foo': 1}

        >>> __set_nested(['foo', 'bar'], 1, {'foo': {'baz': 2}})
        {'foo': {'baz': 2, 'bar': 1}}
    """
    @staticmethod
    def __set_nested(keys, value, my_dict):
        if len(keys) > 1:
            key = keys[0]
            if key in my_dict:
                if isinstance(my_dict[key], dict):
                    new_config = my_dict[key]
                else:
                    new_config = {}
            else:
                new_config = {}
            return {**my_dict, **{key: Config.__set_nested(keys[1:], value, new_config)}}
        elif len(keys) == 1:
            my_dict[keys[0]] = value
            return my_dict
        else:
            raise Exception("No keys were given.")
