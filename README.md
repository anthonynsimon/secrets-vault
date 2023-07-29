# secrets-vault

Simple tool to keep your app secrets encrypted in-repo, decrypt using a `master.key`.

The vault can be YAML (default) or JSON encoded, and is encrypted using [AES-GCM-256 authenticated encryption](https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM).

Inspired by Rails credentials - it pairs nicely with [mrsk](https://mrsk.dev). But it can be used as a standalone CLI tool or as a library. 

## Quick start

1. Install it:
```bash
$ pip install secrets-vault
```

2. Create a new vault:
 ```bash
$ secrets init

Generated new secrets vault at ./secrets.yml.enc
Generated new master key at ./master.key - keep it safe!
 ``` 

3. Open vault in your editor:
```bash
$ secrets edit

# Add your secrets below, comments are supported too.
# dev:
#     secret-key: abc123
#
# database-url: postgres://user:pass@localhost:5432/dev
```

4. Read secrets:

```bash
$ secrets get database-url

> postgres://user:pass@localhost:5432/dev
```

5. Consume secrets as environment variables:

```bash
$ secrets envify production -o dotenv

$ cat .env

> DATABASE_URL=postgres://...
> REDIS_URL=redis://...
> COOKIE_SECRET=abc123
```

**Important:** You should keep the `master.key` secret, do NOT commit it. Ignore it in your `.gitignore` file. The `secrets.yml.enc` file is encrypted and can be committed.

## CLI usage

You can view the help anytime by running `secrets --help`:

```
Usage: secrets [OPTIONS] COMMAND [ARGS]...

  Manage a local secrets vault.

Options:
  -s, --secrets-filepath TEXT     Path to the encrypted secrets vault.
                                  [default: ./secrets.yml.enc]
  -m, --master-key-filepath TEXT  Path to the master.key file.  [default:
                                  ./master.key]
  -f, --format [yaml|json]        Format to use for the secrets vault.
                                  [default: yaml]
  -v, --verbose                   Enable verbose output.
  --help                          Show this message and exit.

Commands:
  del      Delete a secret.
  edit     Open the secrets vault in your configured $EDITOR.
  envify   Prints a provided secret key as one or more env variables.
  get      Get a secret value.
  init     Generate a new secrets vault and master.key pair.
  set      Store a secret.
  version  Show the package version.
```

## Reading secrets

### CLI commands

List all secrets:

```bash
$ secrets get

# Add your secrets below, comments are supported too.
# dev:
#     secret-key: abc123
#
# database-url: postgres://user:pass@localhost:5432/dev
```

Get a secret:

```bash
$ secrets get database-url
> postgres://user:pass@localhost:5432/dev
```

Traverse nested objects:

```bash
$ secrets get

dev:
 secret-key: abc123
 admins: [zero, one, two three]

database-url: postgres://user:pass@localhost:5432/dev
```

```bash
$ secrets get dev.admins.2

> two
```


### In Python

Simply call `get` with the key. Note that if the secret is missing it will return `None`

```python
from secrets_vault import SecretsVault

vault = SecretsVault()

admins = vault.get('dev.admins')
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

# Add your secrets below, comments are supported too.
# dev:
#     secret-key: abc123
#
# database-url: postgres://user:pass@localhost:5432/dev
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

aws-credentials:
    aws-access-key-id: abc123
    aws-secret-access-key: abc456
    
database-url: postgres://user:pass@localhost:5432/dev
```

Envify will print the secrets ready for consumption as environment variables:

```bash
$ secrets envify aws-credentials

AWS_ACCESS_KEY_ID=abc123
AWS_SECRET_ACCESS_KEY=abc456
```

You can also print the entire vault as environment variables:

```bash
$ secrets envify

AWS_CREDENTIALS={"aws-access-key-id": "abc123", "aws-secret-access-key": "abc456"}
DATABASE_URL=postgres://user:pass@localhost:5432/dev
```

The following conventions are applied:
- The key is uppercased
- Dashes are replaced with underscores
- Values are serialized as plain-text (eg. strings and numbers) 
- Objects are JSON encoded (eg. lists and dicts) 

### Consuming the output of envify

You can then use it in your shell like this:

```bash
$ $(secrets envify --export aws-credentials)
$ echo $AWS_ACCESS_KEY_ID

abc123
```

Dump output to a dotenv file:

```bash
$ secrets envify aws-credentials -o dotenv
$ cat .env
> AWS_ACCESS_KEY_ID=abc123
> AWS_SECRET_ACCESS_KEY=abc456
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
  --secrets-filepath ./prod/secrets.yml.enc \
  init
```

This can be used to separate your secrets by environments such as `prod`, `staging`, `dev`, each having with their own key.

### In Python

You can also configure the filepaths at which your `secrets.yml.enc` and `master.key` files are located.

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
