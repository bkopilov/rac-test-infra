import random
import yaml

def generate_mac():
    return "fe:54:00:" + ":".join([('0'+hex(random.randint(0, 30))[2:])[-2:].upper() for _ in range(3)])

def read_tests_params(yaml_file):
    with open(yaml_file) as f:
        config = yaml.safe_load(f)

    return config
