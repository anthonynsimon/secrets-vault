import base64
import logging
import os
import textwrap
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from secrets_vault.exceptions import (
    MasterKeyInvalid,
)

log = logging.getLogger(__name__)


class AES256GCMBackend:
    def __init__(self, master_key=None):
        self.master_key = master_key

    def encrypt(self, contents: bytes) -> bytes:
        try:
            nonce = os.urandom(12)
            key = bytes.fromhex(self.master_key)
            ciphertext = nonce + AESGCM(key).encrypt(nonce, contents, b"")
            encoded = base64.b64encode(ciphertext)
            return "\n".join(textwrap.wrap(encoded.decode("utf8"), width=80)).encode(
                "utf8"
            )
        except (InvalidTag, ValueError, TypeError):
            raise MasterKeyInvalid(
                "The master key is invalid. Make sure it is set and you are using the correct one."
            )

    def decrypt(self, contents: bytes) -> bytes:
        try:
            key = bytes.fromhex(self.master_key)
            unwrapped = contents.replace(b"\n", b"")
            ciphertext = base64.b64decode(unwrapped)
            return AESGCM(key).decrypt(ciphertext[:12], ciphertext[12:], b"")
        except (InvalidTag, ValueError, TypeError):
            raise MasterKeyInvalid(
                "The master key is invalid. Make sure it is set and you are using the correct one."
            )

    @staticmethod
    def generate_master_key() -> str:
        return AESGCM.generate_key(bit_length=256).hex()
