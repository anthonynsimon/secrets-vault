import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path

from secrets_vault.backends import AES256GCMBackend
from secrets_vault.constants import (
    DEFAULT_MASTER_KEY_FILEPATH,
    DEFAULT_SECRETS_FILEPATH,
)
from secrets_vault.exceptions import (
    MasterKeyNotFound,
    SecretsFileNotFound,
    SecretsFileAlreadyExists,
    MalformedSecretsFile,
)

log = logging.getLogger(__name__)


class SecretsVault:
    def __init__(
        self,
        master_key=None,
        secrets_filepath=DEFAULT_SECRETS_FILEPATH,
        master_key_filepath=DEFAULT_MASTER_KEY_FILEPATH,
        backend=AES256GCMBackend,
    ):
        if master_key is None:
            self.master_key = self._load_master_key(master_key_filepath)
        else:
            self.master_key = master_key
        self.secrets_filename = secrets_filepath
        self.backend = backend(self.master_key)
        self.secrets = dict()
        self.load()

    @classmethod
    def create(
        cls,
        secrets_filepath=DEFAULT_SECRETS_FILEPATH,
        master_key_filepath=DEFAULT_MASTER_KEY_FILEPATH,
        backend=AES256GCMBackend,
    ):
        """
        Create a new secrets file and returns the master key - keep it safe!
        """
        cls._prepare_dirs(master_key_filepath, secrets_filepath)

        master_key = backend.generate_master_key()
        with open(master_key_filepath, "w") as fout:
            fout.write(master_key)

        vault = SecretsVault(master_key, secrets_filepath)
        vault.secrets = {"my-user": "foo", "my-password": "supersecret"}
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
        editor = os.environ.get("EDITOR", "").split(" ")  # 'could be "code --wait"'
        if not editor:
            raise RuntimeError("No interactive editor set. Set it as an environment variable 'EDITOR'")

        filedesc, filename = tempfile.mkstemp()

        with open(filedesc, "w+b") as fout:
            fout.write(self._serialize())

        status = subprocess.call([*editor, filename])
        if status != 0:
            raise RuntimeError("Editor returned non-zero status code")

        with open(filename, "rb") as fin:
            try:
                newsecrets = json.loads(fin.read())
            except json.JSONDecodeError as e:
                raise MalformedSecretsFile(f"Could not parse secrets file: {e}")

        if self.secrets == newsecrets:
            log.info("No changes applied")
            return

        self.secrets = newsecrets
        self.save()

    def save(self):
        with open(self.secrets_filename, "wb") as fout:
            fout.write(self.backend.encrypt(self._serialize()))
        log.info(f"Wrote encrypted secrets to {self.secrets_filename}")

    def load(self):
        log.info(f"Loading encrypted secrets from {self.secrets_filename}")
        if not os.path.exists(self.secrets_filename):
            raise SecretsFileNotFound(f"Could not find secrets file {self.secrets_filename}")
        with open(self.secrets_filename, "rb") as fin:
            contents = fin.read()
            if contents:
                self.secrets = json.loads(self.backend.decrypt(contents))
            else:
                self.secrets = dict()

    @staticmethod
    def _load_master_key(master_key_filepath=None) -> str:
        master_key = os.environ.get("MASTER_KEY")
        if not master_key and master_key_filepath and os.path.exists(master_key_filepath):
            with open(Path(master_key_filepath).absolute(), "r") as fin:
                master_key = fin.read().strip()
        if not master_key:
            raise MasterKeyNotFound(
                "Could not find encryption master key. "
                f"Set it as an environment variable 'MASTER_KEY', or in a file '{master_key_filepath}'"
            )
        return master_key

    def _serialize(self) -> bytes:
        return json.dumps(self.secrets, sort_keys=False, indent=4).encode()

    @classmethod
    def _prepare_dirs(cls, master_key_filepath, secrets_filepath):
        if Path(secrets_filepath).exists():
            raise SecretsFileAlreadyExists(f"Secrets file {secrets_filepath} already exists")
        log.info(f"Creating new secrets file {secrets_filepath}")
        Path(master_key_filepath).parent.mkdir(parents=True, exist_ok=True)
        Path(secrets_filepath).parent.mkdir(parents=True, exist_ok=True)
        Path(secrets_filepath).touch()
