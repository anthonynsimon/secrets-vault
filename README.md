# secrets-vault

Simple encrypted secrets for Python.

Inspired by Rails encrypted secrets, but for Python. It can be used as a standalone CLI tool or as a library. 

The vault is JSON encoded and encrypted using [symmetric encryption](https://cryptography.io/en/latest/fernet/).

## Quick start

1. Install `pip install secrets-vault`.
2. Run `secrets-vault init`.
3. Two files will be created: `master.key` and `secrets.json.enc`.
4. You can now edit your secrets by running `secrets-vault edit`, or list them via `secrets-vault get`.

**Important:** Keep the `master.key` safe. Do NOT commit it to VCS. The `secrets.json.enc` file is safe to commit.


## Reading secrets via CLI

List all secrets:

```bash
$ secrets-vault get

> my-user: foo
> my-password: supersecret
```

Get one secret:

```bash
$ secrets-vault get my-password

> supersecret
```


## Reading secrets from code

```python
from secrets_vault import SecretsVault


vault = SecretsVault()

password = vault.get('my-password')

```


## Editing secrets

To edit secrets, run `secrets-vault edit`, the file will be decrypted and your editor will open.

Any saved changes will be encrypted and saved to the file on disk when you close the editor.


## Providing the master.key file

### File on disk
By default, the vault will look for the master key in a file located at `./master.key`.

### Environment variable
You can also provide it via an environment variable `MASTER_KEY`. For example:

```bash
MASTER_KEY=my-super-secret-master-key secrets-vault edit
```

### In application code

You can load the master_key from anywhere else and provide it when initializing the class:

```python
from secrets_vault import SecretsVault

# Load from somewhere else
master_key = 'my-super-secret-master-key'

vault = SecretsVault(master_key=master_key)
```


### Configuring the default filepaths

You can also configure the filepaths at which your `secrets.json.enc` and `master.key` files are located.

```python
from secrets_vault import SecretsVault

vault = SecretsVault(master_key_filepath=..., secrets_filepath=...)
```


## Changelog

### 0.1.2
- Initial release


## Security Disclosure

If you discover any issue regarding security, please disclose the information responsibly by sending an email to [dyer.linseed0@icloud.com](mailto:dyer.linseed0@icloud.com). Do NOT create a Issue on the GitHub repo.


## Contributing

Please check for any existing issues before openning a new Issue. If you'd like to work on something, please open a new Issue describing what you'd like to do before submitting a Pull Request.


## License

See [LICENSE](https://github.com/anthonynsimon/secrets-vault/blob/master/LICENSE).
