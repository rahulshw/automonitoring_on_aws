import json

CONFIG_FILE = "config.json"

def get_config(config_file=CONFIG_FILE):
    with open(config_file) as f:
        config = json.load(f)
    return config
