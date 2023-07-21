# secrets-vault

Simple encrypted secrets for Python.

Inspired by Rails encrypted secrets. It can be used as a standalone CLI tool or as a library. 

The vault is JSON encoded and encrypted using [AES-GCM-256 authenticated encryption](https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM).

## Quick start

1. Install it:
```bash
$ pip install secrets-vault
```

2. Create a new vault:
 ```bash
 $ secrets init
 
 Generated new secrets vault at ./secrets.json.enc
 Generated new master key at ./master.key - keep it safe!
 ``` 

3. Edit secrets:
```bash
$ secrets edit

>> Opening secrets file in editor...
{
  "foo": "bar"
}
```

4. Read secrets:

```bash
# Via CLI
$ secrets get foo
> bar
```

```python
# In Python
from secrets_vault import SecretsVault

vault = SecretsVault()
foo = vault.get('foo')
```

**Important:** You should keep the `master.key` secret, do NOT commit it. Ignore it in your `.gitignore` file. The `secrets.json.enc` file is encrypted and can be committed.

## CLI usage

You can view the help anytime by running `secrets --help`:

```
Usage: secrets [OPTIONS] COMMAND [ARGS]...

  Manage a local secrets vault.

Options:
  -s, --secrets-filepath TEXT     Path to the encrypted secrets vault.
  -m, --master-key-filepath TEXT  Path to the master.key file.
  --help                          Show this message and exit.

Commands:
  del      Delete a secret.
  edit     Open the secrets vault in your configured $EDITOR.
  envify   Prints a provided secret key as one or more env variables.
  get      Get one or more secret values.
  init     Generate a new secrets vault and master.key pair.
  set      Store a secret.
  version  Show the package version.
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

Simply call `get` with the key. Note that if the secret is missing it will return `None`

```python
from secrets_vault import SecretsVault

vault = SecretsVault()

password = vault.get('my-password')
```


## Editing secrets

### CLI command

You can set secrets from the CLI with a key and value:

```bash
$ secrets set foo bar
```

### Interactive editor

To edit secrets, run `secrets edit`, the file will be decrypted and your editor will open.

```bash
$ secrets edit

>> Opening secrets file in editor...
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

When a master key is provided via an environment variable, it takes precedence over the file on disk.


### In Python

You can load the master_key from anywhere else and provide it when initializing the class:

```python
from secrets_vault import SecretsVault

# Load from somewhere else
master_key = 'my-super-secret-master-key'

vault = SecretsVault(master_key=master_key)
```

The order of precedence for the master key is:
1. Provided via the constructor
2. Provided via the `MASTER_KEY` environment variable
3. Loaded from the file on disk

## Configuring the default filepaths

### CLI command

You can also provide them as a CLI arguments before the command:

```bash
$ secrets \
  --master-key-filepath ./prod/master.key \
  --secrets-filepath ./prod/secrets.json.enc \
  init
```

This can be used to separate your secrets by environments such as `prod`, `staging`, `dev`, each having with their own key.

### In Python

You can also configure the filepaths at which your `secrets.json.enc` and `master.key` files are located.

```python
from secrets_vault import SecretsVault

vault = SecretsVault(master_key_filepath=..., secrets_filepath=...)
```

## Changelog

See [CHANGELOG](https://github.com/anthonynsimon/secrets-vault/blob/master/CHANGELOG.md) for the list of releases.


## Security Disclosure

If you discover any issue regarding security, please disclose the information responsibly by sending an email to [dyer.linseed0@icloud.com](mailto:dyer.linseed0@icloud.com). Do NOT create a Issue on the GitHub repo.


## Contributing

Please check for any existing issues before openning a new Issue. If you'd like to work on something, please open a new Issue describing what you'd like to do before submitting a Pull Request.


## License

See [LICENSE](https://github.com/anthonynsimon/secrets-vault/blob/master/LICENSE).
