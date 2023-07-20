# secrets-vault

Simple encrypted secrets for Python.

Inspired by Rails encrypted secrets, but for Python. It can be used as a standalone CLI tool or as a library. 

The vault is JSON encoded and encrypted using [symmetric encryption](https://cryptography.io/en/latest/fernet/).

## Quick start

1. Install `pip install secrets-vault`.
2. Run `secrets init`.
3. Two files will be created: `master.key` and `secrets.json.enc`.
4. You can now edit your secrets by running `secrets edit`, or list them via `secrets get`.

**Important:** Keep the `master.key` safe. Do NOT commit it to VCS. The `secrets.json.enc` file is safe to commit.


## CLI usage

You can view the help anytime by running `secrets --help`:

```
Usage: secrets [OPTIONS] COMMAND [ARGS]...

  Manage a local secrets vault.

Options:
  -m, --master-key-filepath TEXT  Path to the master.key file.
  -s, --secrets-filepath TEXT     Path to the encrypted secrets vault.
  --help                          Show this message and exit.

Commands:
  del     Delete a secret.
  edit    Open the secrets vault in your configured $EDITOR.
  envify  Prints a provided secret key as one or more env variables.
  get     Get one or more secret values.
  init    Generate a new secrets vault and master.key pair.
  set     Store a secret.
```

## Reading secrets

### CLI commands

List all secrets:

```bash
$ secrets get
> my-user: foo
> my-password: supersecret
```

Get one secret:

```bash
$ secrets get my-password
> supersecret
```

Get multiple secrets:

```bash
$ secrets get my-user my-password
> my-user: foo
> my-password: supersecret
```


### In Python

```python
from secrets_vault import SecretsVault

vault = SecretsVault()

password = vault.get('my-password')
```


## Editing secrets

### CLI command

You can also set secrets from the CLI with a key and value:

```bash
$ secrets set foo bar
```

### Interactive editor

To edit secrets, run `secrets edit`, the file will be decrypted and your editor will open.

```bash
$ secrets edit

>>> Opening secrets file in editor...
{
  "foo": "bar"
}
```

Any saved changes will be encrypted and saved to the file on disk when you close the editor.

### In Python

You can also edit secrets from code:

```python
from secrets_vault import SecretsVault

vault = SecretsVault()
vault.set('foo', 'bar')
vault.save()
```

## Deleting secrets

### CLI command

You can delete secrets from the CLI with a key:

```bash
$ secrets del foo
```

### In Python

You can achieve the same in Python like this:

```python
from secrets_vault import SecretsVault

vault = SecretsVault()
vault.delete('foo')
vault.save()
```


## Printing secrets as environment variables

Sometimes you may want to print a secret as environment variables. It will also apply if you have nested objects. You can do so by running:

```bash
$ secrets edit

{
  "aws-credentials": {
    "AWS_ACCESS_KEY_ID": "...",
    "AWS_SECRET_ACCESS_KEY": "..."
  }
}
```

Get will print the secrets as-is:

```bash
$ secrets get aws-credentials
> {"AWS_ACCESS_KEY_ID": "...", "AWS_SECRET_ACCESS_KEY": "..."}
```

Envify will print the secrets ready for consumption as environment variables:

```bash
$ secrets envify aws-credentials
> AWS_ACCESS_KEY_ID=...
> AWS_SECRET_ACCESS_KEY=...
```

## Providing the master.key file

### File on disk
By default, the vault will look for the master key in a file located at `./master.key`.

### Environment variable
You can also provide it via an environment variable `MASTER_KEY`. For example:

```bash
MASTER_KEY=my-super-secret-master-key secrets edit
```

### In Python

You can load the master_key from anywhere else and provide it when initializing the class:

```python
from secrets_vault import SecretsVault

# Load from somewhere else
master_key = 'my-super-secret-master-key'

vault = SecretsVault(master_key=master_key)
```


## Configuring the default filepaths

### CLI command
You can also provide them as a CLI argument before any command:

```bash
$ secrets --master-key-filepath foo1 --secrets-filepath foo2 edit
```

### In Python

You can also configure the filepaths at which your `secrets.json.enc` and `master.key` files are located.

```python
from secrets_vault import SecretsVault

vault = SecretsVault(master_key_filepath=..., secrets_filepath=...)
```


## Changelog

### 0.1.6
- Fix requirements not listed in package

### 0.1.5
- Add envify command
- Refactor CLI tool
- Breaking Python API changes: persist() has been renamed to save(), and init() has been renamed to create().

### 0.1.4
- Add del command

### 0.1.3
- Add set command

### 0.1.2
- Initial release


## Security Disclosure

If you discover any issue regarding security, please disclose the information responsibly by sending an email to [dyer.linseed0@icloud.com](mailto:dyer.linseed0@icloud.com). Do NOT create a Issue on the GitHub repo.


## Contributing

Please check for any existing issues before openning a new Issue. If you'd like to work on something, please open a new Issue describing what you'd like to do before submitting a Pull Request.


## License

See [LICENSE](https://github.com/anthonynsimon/secrets-vault/blob/master/LICENSE).
