import os
import logging
import configparser


def get_config_options(file="config.cfg"):
    config = configparser.ConfigParser()
    config.read(file)
    config_options = {}
    for section in config.sections():
        for (key, value) in config.items(section):
            config_options[f"{section.lower()}_{key.lower()}"] = value
    return config_options


def get_env_vars(env_var_keys):
    env_vars = {}
    for key in env_var_keys:
        if key in os.environ:
            env_vars[key] = os.environ[key].rstrip()
        else:
            raise ValueError(key)
    return env_vars


def get_logger(stream=True, file=False, log_file=None):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(levelname)s: [%(process)d] %(message)s", "%Y-%m-%d %H:%M:%S")
    if not logger.handlers:
        if stream:
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        if file and log_file is not None:
            handler = logging.FileHandler(log_file)
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    return logger
