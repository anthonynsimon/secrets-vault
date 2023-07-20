import json
import logging
import os
import tempfile
from pathlib import Path
from subprocess import call

from cryptography.fernet import Fernet, InvalidToken

from secrets_vault.constants import (
    DEFAULT_MASTER_KEY_FILEPATH,
    DEFAULT_SECRETS_FILEPATH,
)
from secrets_vault.exceptions import (
    MasterKeyNotFound,
    MasterKeyInvalid,
    SecretsFileNotFound,
    SecretsFileAlreadyExists,
)

log = logging.getLogger(__name__)


class SecretsVault:
    def __init__(
        self,
        master_key=None,
        secrets_filepath=DEFAULT_SECRETS_FILEPATH,
        master_key_filepath=DEFAULT_MASTER_KEY_FILEPATH,
    ):
        if master_key is None:
            master_key = self._load_master_key(master_key_filepath)
        try:
            self.fernet = Fernet(master_key)
            self.secrets_filename = secrets_filepath
            self.secrets = dict()
            self._load_secrets()
        except InvalidToken:
            raise MasterKeyInvalid("Master key is malformed or invalid")

    @staticmethod
    def create(
        secrets_filepath=DEFAULT_SECRETS_FILEPATH,
        master_key_filepath=DEFAULT_MASTER_KEY_FILEPATH,
    ):
        """
        Create a new secrets file and returns the master key - keep it safe!
        """
        if Path(secrets_filepath).exists():
            raise SecretsFileAlreadyExists(f"Secrets file {secrets_filepath} already exists")

        log.info(f"Creating new secrets file {secrets_filepath}")
        Path(master_key_filepath).parent.mkdir(parents=True, exist_ok=True)
        Path(secrets_filepath).parent.mkdir(parents=True, exist_ok=True)
        Path(secrets_filepath).touch()

        master_key = Fernet.generate_key().decode()
        with open(master_key_filepath, "w") as fout:
            fout.write(master_key)

        vault = SecretsVault(master_key, secrets_filepath)
        vault.set("my-user", "foo")
        vault.set("my-password", "supersecret")
        vault.save()

        return vault, master_key

    def require(self, key):
        return self.secrets[key]

    def get(self, key, default=None):
        return self.secrets.get(key, default)

    def set(self, key, value):
        self.secrets[key] = value

    def delete(self, key):
        if key in self.secrets:
            del self.secrets[key]

    def edit_secrets(self):
        """
        Decrypts and opens the secrets file in an editor. On save, the file is encrypted again.
        """
        self._load_secrets()
        EDITOR = os.environ.get("EDITOR", "vim").split(" ")  # 'could be "code --wait"'
        with tempfile.NamedTemporaryFile(suffix=".tmp.yml") as tf:
            tf.write(self._serialize())
            tf.flush()
            call([*EDITOR, tf.name])
            tf.seek(0)
            newsecrets = json.loads(tf.read())

        if self.secrets == newsecrets:
            log.info("No changes applied")
            return
        self.secrets = newsecrets
        self.save()

    def save(self):
        with open(self.secrets_filename, "wb") as fout:
            fout.write(self.fernet.encrypt(self._serialize()))
        log.info(f"Wrote encrypted secrets to {self.secrets_filename}")

    @staticmethod
    def _load_master_key(master_key_filepath=None):
        master_key = os.environ.get("MASTER_KEY")
        if not master_key and master_key_filepath and os.path.exists(master_key_filepath):
            with open(Path(master_key_filepath).absolute()) as fin:
                master_key = fin.read().strip()
        if not master_key:
            raise MasterKeyNotFound(
                "Could not find encryption master key. "
                f"Set it as an environment variable 'MASTER_KEY', or in a file '{master_key_filepath}'"
            )
        return master_key

    def _load_secrets(self):
        log.info(f"Loading encrypted secrets from {self.secrets_filename}")
        if not os.path.exists(self.secrets_filename):
            raise SecretsFileNotFound(f"Could not find secrets file {self.secrets_filename}")
        with open(self.secrets_filename, "r") as fin:
            contents = fin.read()
            if contents:
                self.secrets = json.loads(self.fernet.decrypt(contents))
            else:
                self.secrets = dict()

    def _serialize(self):
        return json.dumps(self.secrets, sort_keys=False, indent=4).encode()
