__all__ = ["yaml"]

from ruamel.yaml import YAML

# Configure roundtrip YAML formatter
yaml = YAML(typ="rt")
yaml.width = 4096
