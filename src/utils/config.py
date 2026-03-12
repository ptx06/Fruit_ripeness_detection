import yaml
from pathlib import Path

def load_config(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def save_config(config, save_path):
    with open(save_path, 'w') as f:
        yaml.dump(config, f)