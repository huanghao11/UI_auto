import yaml

config_path = "D:\\UI_auto\\config.yaml"

def read_yaml(key):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    value = config[key]

    return value