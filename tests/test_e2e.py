import os
from pathlib import Path

from secrets_vault import SecretsVault, exceptions

BASE_DIR = Path(__file__).parent
TEST_DATA_DIR = BASE_DIR / "test-data"


def test_create():
    vault, master_key = SecretsVault.create(
        secrets_filepath=TEST_DATA_DIR / "secrets-1.json.enc",
        master_key_filepath=TEST_DATA_DIR / "master-1.key",
    )

    assert os.path.exists(TEST_DATA_DIR / "secrets-1.json.enc")
    assert os.path.exists(TEST_DATA_DIR / "master-1.key")
    assert master_key is not None and len(master_key) == 64
    with open(TEST_DATA_DIR / "master-1.key", "rb") as fin:
        assert fin.read().decode() == master_key

    vault = SecretsVault(
        secrets_filepath=TEST_DATA_DIR / "secrets-1.json.enc",
        master_key_filepath=TEST_DATA_DIR / "master-1.key",
    )
    assert vault.get("my-password") == "supersecret"


def test_requires_master_key():
    SecretsVault.create(
        secrets_filepath=TEST_DATA_DIR / "secrets-2.json.enc",
        master_key_filepath=TEST_DATA_DIR / "master-2.key",
    )

    try:
        SecretsVault(
            secrets_filepath=TEST_DATA_DIR / "secrets-2.json.enc",
            master_key_filepath=TEST_DATA_DIR / "master-456.key",
        )
        assert False, "Should throw"
    except Exception as e:
        assert isinstance(e, exceptions.MasterKeyNotFound)


def test_provides_master_key_via_env_var():
    SecretsVault.create(
        secrets_filepath=TEST_DATA_DIR / "secrets-2a.json.enc",
        master_key_filepath=TEST_DATA_DIR / "master-2a.key",
    )

    with open(TEST_DATA_DIR / "master-2a.key", "rb") as fin:
        master_key = fin.read().decode()
        os.environ["MASTER_KEY"] = master_key

    vault = SecretsVault(
        secrets_filepath=TEST_DATA_DIR / "secrets-2a.json.enc",
        master_key_filepath=None,
    )
    assert vault.get("my-password") == "supersecret"

    # Cleanup to not affect other tests
    del os.environ["MASTER_KEY"]


def test_requires_secrets_file():
    SecretsVault.create(
        secrets_filepath=TEST_DATA_DIR / "secrets-3.json.enc",
        master_key_filepath=TEST_DATA_DIR / "master-3.key",
    )

    try:
        SecretsVault(
            secrets_filepath=TEST_DATA_DIR / "secrets-456.json.enc",
            master_key_filepath=TEST_DATA_DIR / "master-3.key",
        )
        assert False, "Should throw"
    except Exception as e:
        assert isinstance(e, exceptions.SecretsFileNotFound)


def test_save():
    SecretsVault.create(
        secrets_filepath=TEST_DATA_DIR / "secrets-4.json.enc",
        master_key_filepath=TEST_DATA_DIR / "master-4.key",
    )

    vault = SecretsVault(
        secrets_filepath=TEST_DATA_DIR / "secrets-4.json.enc",
        master_key_filepath=TEST_DATA_DIR / "master-4.key",
    )

    assert vault.get("my-password") == "supersecret"
    assert vault.get("hello") is None
    assert vault.get("nested") is None

    vault.set("hello", "world")
    vault.set("nested", {"object": "value"})
    vault.save()

    assert vault.get("hello") == "world"
    assert vault.get("nested") == {"object": "value"}


def test_large_secrets_file():
    SecretsVault.create(
        secrets_filepath=TEST_DATA_DIR / "secrets-5.json.enc",
        master_key_filepath=TEST_DATA_DIR / "master-5.key",
    )

    vault = SecretsVault(
        secrets_filepath=TEST_DATA_DIR / "secrets-5.json.enc",
        master_key_filepath=TEST_DATA_DIR / "master-5.key",
    )

    for i in range(10000):
        vault.set(f"key-{i}", f"value-{i}")
    vault.save()

    for i in range(10000):
        assert vault.get(f"key-{i}") == f"value-{i}"


def test_wrong_key():
    SecretsVault.create(
        secrets_filepath=TEST_DATA_DIR / "secrets-6.json.enc",
        master_key_filepath=TEST_DATA_DIR / "master-6.key",
    )

    try:
        SecretsVault(
            secrets_filepath=TEST_DATA_DIR / "secrets-6.json.enc",
            master_key_filepath=TEST_DATA_DIR / "master-5.key",
        )
        assert False, "Should throw"
    except Exception as e:
        assert isinstance(e, exceptions.MasterKeyInvalid)
