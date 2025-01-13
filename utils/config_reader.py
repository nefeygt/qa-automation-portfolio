import yaml
import os

def read_config():
    """Read configuration from YAML file"""
    # Determine which config file to use
    config_file = 'config/config.ci.yaml' if os.getenv('CI') else 'config/config.yaml'
    
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)