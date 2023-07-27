import json
import logging
import os
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path

import pydash
from ruamel.yaml import YAML

from secrets_vault import exceptions, constants

log = logging.getLogger(__name__)


class SecretsVault:
    def __init__(
        self,
        master_key=None,
        secrets_filepath=constants.DEFAULT_SECRETS_FILEPATH,
        master_key_filepath=constants.DEFAULT_MASTER_KEY_FILEPATH,
        backend=constants.DEFAULT_BACKEND,
        file_format=constants.DEFAULT_FILE_FORMAT,
    ):
        assert file_format in {"yaml", "json"}, "Format must be either 'yaml' or 'json'"
        self.file_format = file_format

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
        secrets_filepath=constants.DEFAULT_SECRETS_FILEPATH,
        master_key_filepath=constants.DEFAULT_MASTER_KEY_FILEPATH,
        backend=constants.AES256GCMBackend,
        file_format=constants.DEFAULT_FILE_FORMAT,
    ):
        """
        Create a new secrets file and returns the master key - keep it safe!
        """
        cls._prepare_dirs(master_key_filepath, secrets_filepath)

        master_key = backend.generate_master_key()
        with open(master_key_filepath, "w") as fout:
            fout.write(master_key)

        vault = SecretsVault(master_key=master_key, secrets_filepath=secrets_filepath, file_format=file_format)

        example = cls._get_example(file_format)

        vault.secrets = vault._deserialize(example.encode())
        vault.save()

        return vault, master_key

    def require(self, key):
        value = self.get(key, default=constants.UNSET)
        if value == constants.UNSET:
            raise KeyError(f"Secret {key} not found in secrets vault")
        return value

    def get(self, key, default=None):
        return pydash.get(self.secrets, key, default)

    def set(self, key, value):
        pydash.set_(self.secrets, key, value)
        return self

    def delete(self, key):
        pydash.unset(self.secrets, key)
        return self

    def edit_secrets(self):
        """
        Decrypts and opens the secrets file in an editor. On save, the file is encrypted again.
        """
        editor = os.environ.get("EDITOR", "").split(" ")  # 'could be "code --wait"'
        if not editor:
            raise RuntimeError("No interactive editor set. Set it as an environment variable 'EDITOR'")

        filedesc, filename = tempfile.mkstemp(suffix=".yml")
        try:
            with open(filedesc, "w+b") as fout:
                fout.write(self._serialize(self.secrets))

            status = subprocess.call([*editor, filename])
            if status != 0:
                raise RuntimeError("Editor returned non-zero status code")

            with open(filename, "rb") as fin:
                try:
                    newsecrets = self._deserialize(fin.read())
                except Exception as e:
                    raise exceptions.MalformedSecretsFile(f"Could not parse secrets file: {e}")

            if self._serialize(newsecrets) == self._serialize(self.secrets):
                log.info("No changes detected")
                return

            self.secrets = newsecrets
            self.save()
        finally:
            os.remove(filename)

    def save(self):
        with open(self.secrets_filename, "wb") as fout:
            fout.write(self.backend.encrypt(self._serialize(self.secrets)))
        log.info(f"Wrote encrypted secrets to {self.secrets_filename}")

    def load(self):
        log.info(f"Loading encrypted secrets from {self.secrets_filename}")
        if not os.path.exists(self.secrets_filename):
            raise exceptions.SecretsFileNotFound(f"Could not find secrets file {self.secrets_filename}")
        with open(self.secrets_filename, "rb") as fin:
            contents = fin.read()
            if contents:
                self.secrets = self._deserialize(self.backend.decrypt(contents))
            else:
                self.secrets = dict()

    @staticmethod
    def _load_master_key(master_key_filepath=None) -> str:
        master_key = os.environ.get("MASTER_KEY")
        if not master_key and master_key_filepath and os.path.exists(master_key_filepath):
            with open(Path(master_key_filepath).absolute(), "r") as fin:
                master_key = fin.read().strip()
        if not master_key:
            raise exceptions.MasterKeyNotFound(
                "Could not find encryption master key. "
                f"Set it as an environment variable 'MASTER_KEY', or in a file '{master_key_filepath}'"
            )
        return master_key

    def _deserialize(self, data: bytes) -> dict:
        if self.file_format in {"yaml", "json"}:
            yaml = YAML(typ="rt")
            fin = BytesIO(data)
            return yaml.load(fin)
        raise NotImplementedError(f"Unknown file_format {self.file_format}")

    def _serialize(self, data: dict) -> bytes:
        if self.file_format == "json":
            return json.dumps(data, indent=4).encode()
        elif self.file_format == "yaml":
            yaml = YAML(typ="rt")
            fout = BytesIO()
            yaml.dump(data, fout)
            result = fout.getvalue()
            fout.close()
            return result

        raise NotImplementedError(f"Unknown file_format {self.file_format}")

    @classmethod
    def _prepare_dirs(cls, master_key_filepath, secrets_filepath):
        if Path(secrets_filepath).exists():
            raise exceptions.SecretsFileAlreadyExists(f"Secrets file {secrets_filepath} already exists")
        log.info(f"Creating new secrets file {secrets_filepath}")
        Path(master_key_filepath).parent.mkdir(parents=True, exist_ok=True)
        Path(secrets_filepath).parent.mkdir(parents=True, exist_ok=True)
        Path(secrets_filepath).touch()

    @classmethod
    def _get_example(cls, file_format):
        if file_format == "json":
            return constants.EXAMPLE_SECRETS_JSON
        elif file_format == "yaml":
            return constants.EXAMPLE_SECRETS_YAML
