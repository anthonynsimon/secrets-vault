import json

from secrets_vault.backends import AES256GCMBackend

DEFAULT_FILE_FORMAT = "yaml"
DEFAULT_MASTER_KEY_FILEPATH = "./master.key"
DEFAULT_SECRETS_FILEPATH = "./secrets.yml.enc"
DEFAULT_BACKEND = AES256GCMBackend
UNSET = object()

EXAMPLE_SECRETS_YAML = """
# Add your secrets below, comments are supported too.
# app:
#     secret-key: abc123

database-url: postgres://user:pass@localhost:5432/dev
""".strip()

EXAMPLE_SECRETS_JSON = json.dumps(
    {"app": {"secret-key": "abc123"}, "database-url": "postgres://user:pass@localhost:5432/dev"}
)
