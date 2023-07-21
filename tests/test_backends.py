from secrets_vault import exceptions
from secrets_vault.backends import AES256GCMBackend

backend = AES256GCMBackend


def test_generate_key():
    key = backend.generate_master_key()
    assert len(key) == 64

    # check uniqueness
    keys = set(key)
    for _ in range(int(100e3)):
        key = backend.generate_master_key()
        assert key not in keys
        keys.add(key)


def test_encrypt():
    key = backend.generate_master_key()
    cipher = backend(key)
    ct = cipher.encrypt(b"hello world")
    assert ct != b"hello world"

    # check cipher text and nonce uniqueness
    results = set(ct)
    nonces = set(ct[:12])
    for _ in range(int(100e3)):
        ct = cipher.encrypt(b"hello world")
        nonce = ct[:12]
        assert ct not in results
        assert nonce not in nonces
        results.add(ct)
        nonces.add(nonce)


def test_decrypt():
    key = backend.generate_master_key()
    cipher = backend(key)
    ct = cipher.encrypt(b"hello world")
    contents = cipher.decrypt(ct)
    assert contents == b"hello world"


def test_wrong_key():
    key = backend.generate_master_key()
    other = backend.generate_master_key()
    cipher = backend(key)
    ct = cipher.encrypt(b"hello world")

    try:
        backend(other).decrypt(ct)
        assert False, "Should throw"
    except Exception as e:
        assert isinstance(e, exceptions.MasterKeyInvalid)


def test_missing_key():
    key = backend.generate_master_key()
    cipher = backend(key)
    ct = cipher.encrypt(b"hello world")

    try:
        backend(None).decrypt(ct)
        assert False, "Should throw"
    except Exception as e:
        assert isinstance(e, exceptions.MasterKeyInvalid)


def test_empty_key():
    key = backend.generate_master_key()
    cipher = backend(key)
    ct = cipher.encrypt(b"hello world")

    try:
        backend("").decrypt(ct)
        assert False, "Should throw"
    except Exception as e:
        assert isinstance(e, exceptions.MasterKeyInvalid)
