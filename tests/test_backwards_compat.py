import base64
import json

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def test_vault_can_be_read_without_lib():
    with open("tests/fixtures/master.key", "rb") as fin:
        master_key = str(fin.read().decode())

    with open("tests/fixtures/secrets.json.enc", "rb") as fin:
        encrypted_blob = str(fin.read().decode())

    key = bytearray.fromhex(master_key)
    ciphertext = base64.b64decode(encrypted_blob)
    decrypted = AESGCM(key).decrypt(ciphertext[:12], ciphertext[12:], b"")
    deserialized = json.loads(decrypted.decode())

    assert deserialized == {
        "my-user": "foo",
        "my-password": "supersecret",
    }
