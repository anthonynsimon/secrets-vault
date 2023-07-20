import json

import click

from secrets_vault import SecretsVault, exceptions, constants, __version__

common_options = [
    click.option(
        "-s",
        "--secrets-filepath",
        default=constants.DEFAULT_SECRETS_FILEPATH,
        help="Path to the encrypted secrets vault.",
    ),
    click.option(
        "-m",
        "--master-key-filepath",
        default=constants.DEFAULT_MASTER_KEY_FILEPATH,
        help="Path to the master.key file.",
    ),
]


def add_options(options):
    def _add_options(func):
        for option in options:
            func = option(func)
        return func

    return _add_options


def serialize(v):
    if not v:
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return str(v)
    return json.dumps(v, default=str, sort_keys=False)


@click.group(help="Manage a local secrets vault.")
@add_options(common_options)
def cli(**kwargs):
    pass


@cli.command(help="Show the package version.")
def version(**kwargs):
    click.echo(f"secrets-vault v{__version__}")


@cli.command(
    help="Generate a new secrets vault and master.key pair. If a secrets vault already exists, this will abort."
)
@add_options(common_options)
def init(**kwargs):
    try:
        SecretsVault.create(
            secrets_filepath=kwargs["secrets_filepath"], master_key_filepath=kwargs["master_key_filepath"]
        )
        click.echo(f"Generated new secrets vault at {kwargs['secrets_filepath']}")
        click.echo(f"Generated new master key at {kwargs['master_key_filepath']}")
    except exceptions.SecretsFileAlreadyExists:
        print("Secrets file already exists, aborting...")
        exit(1)


def with_vault(func, secrets_filepath, master_key_filepath):
    try:
        vault = SecretsVault(secrets_filepath=secrets_filepath, master_key_filepath=master_key_filepath)
        func(vault)
        exit(0)
    except exceptions.MasterKeyNotFound:
        click.echo(
            f"No master key found. Set it via the environment variable 'MASTER_KEY', or in a file at '{constants.DEFAULT_MASTER_KEY_FILEPATH}'"
        )
    except exceptions.SecretsFileNotFound:
        click.echo("Secrets file not found, aborting...")
    exit(1)


@cli.command(
    help="Get one or more secret values. If none are specified, all secrets are printed (eg. `secrets get`). You can also provide multiple keys to retrive more than one secret at a time (eg. secrets get foo1 foo2 foo3)."
)
@add_options(common_options)
@click.argument("key", required=False, nargs=-1)
def get(key, **kwargs):
    def handler(vault):
        if key:
            if len(key) == 1:
                click.echo(serialize(vault.get(key[0])))
            else:
                for k in key:
                    click.echo(f"{k}: {serialize(vault.get(k))}")
        else:
            for k, v in vault.secrets.items():
                click.echo(f"{k}: {serialize(v)}")

    with_vault(
        handler,
        secrets_filepath=kwargs["secrets_filepath"],
        master_key_filepath=kwargs["master_key_filepath"],
    )


@cli.command(
    help="Prints a provided secret key as one or more env variables. In case the value is a nested object, it will flatten the key=value pairs."
)
@add_options(common_options)
@click.argument("key")
def envify(key, **kwargs):
    def handler(vault):
        value = vault.get(key)
        if isinstance(value, dict):
            for k, v in value.items():
                click.echo(f"{k}={serialize(v)}")
        else:
            click.echo(f"{key}={serialize(value)}")

    with_vault(
        handler,
        secrets_filepath=kwargs["secrets_filepath"],
        master_key_filepath=kwargs["master_key_filepath"],
    )


@cli.command(
    help="Store a secret. If the secret already exists, it will be overwritten. For example: `secrets set foo bar`"
)
@add_options(common_options)
@click.argument("key")
@click.argument("value")
def set(key, value, **kwargs):
    def handler(vault):
        vault.set(key, value)
        vault.save()

    with_vault(
        handler,
        secrets_filepath=kwargs["secrets_filepath"],
        master_key_filepath=kwargs["master_key_filepath"],
    )


@cli.command("del", help="Delete a secret. For example: `secrets del foo`")
@add_options(common_options)
@click.argument("key")
def delete(key, **kwargs):
    def handler(vault):
        vault.delete(key)
        vault.save()

    with_vault(
        handler,
        secrets_filepath=kwargs["secrets_filepath"],
        master_key_filepath=kwargs["master_key_filepath"],
    )


@cli.command(help="Open the secrets vault in your configured $EDITOR.")
@add_options(common_options)
def edit(**kwargs):
    def handler(vault):
        vault.edit_secrets()

    with_vault(
        handler,
        secrets_filepath=kwargs["secrets_filepath"],
        master_key_filepath=kwargs["master_key_filepath"],
    )


if __name__ == "__main__":
    cli()
