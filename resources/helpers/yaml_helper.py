import yaml


def to_dict(yaml_file):
    with open(yaml_file, 'rt') as f:
        output = yaml.safe_load(f.read())
    return output
