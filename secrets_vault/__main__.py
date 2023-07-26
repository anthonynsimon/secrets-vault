import json
import logging

import click

from secrets_vault import SecretsVault, exceptions, constants, __version__


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
@click.option(
    "-s",
    "--secrets-filepath",
    default=constants.DEFAULT_SECRETS_FILEPATH,
    help="Path to the encrypted secrets vault.",
    show_default=True,
)
@click.option(
    "-m",
    "--master-key-filepath",
    default=constants.DEFAULT_MASTER_KEY_FILEPATH,
    help="Path to the master.key file.",
    show_default=True,
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output.",
)
@click.pass_context
def cli(ctx, **kwargs):
    ctx.obj = kwargs
    logging.basicConfig(level=logging.INFO if kwargs["verbose"] else logging.ERROR)


@cli.command(help="Show the package version.")
@click.pass_context
def version(ctx):
    click.echo(f"secrets-vault v{__version__}")


@cli.command(
    help="Generate a new secrets vault and master.key pair. If a secrets vault already exists, this will abort."
)
@click.pass_context
def init(ctx):
    try:
        SecretsVault.create(
            secrets_filepath=ctx.obj["secrets_filepath"], master_key_filepath=ctx.obj["master_key_filepath"]
        )
        click.echo(f"Generated new secrets vault at {ctx.obj['secrets_filepath']}")
        click.echo(f"Generated new master key at {ctx.obj['master_key_filepath']} - keep it safe!")
    except exceptions.SecretsFileAlreadyExists:
        print("Secrets file already exists, aborting...")
        exit(1)


def with_vault(ctx, func):
    try:
        vault = SecretsVault(
            secrets_filepath=ctx.obj["secrets_filepath"], master_key_filepath=ctx.obj["master_key_filepath"]
        )
        func(vault)
    except (
        exceptions.MasterKeyNotFound,
        exceptions.SecretsFileNotFound,
        exceptions.MasterKeyInvalid,
        exceptions.MalformedSecretsFile,
    ) as e:
        click.echo(str(e))
        exit(1)


@cli.command(
    help="Get one or more secret values. If none are specified, all secrets are printed (eg. `secrets get`). You can also provide multiple keys to retrive more than one secret at a time (eg. secrets get foo1 foo2 foo3)."
)
@click.argument("key", required=False, nargs=-1)
@click.pass_context
def get(ctx, key):
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

    with_vault(ctx, handler)


@cli.command(
    help="Prints a provided secret key as one or more env variables. In case the value is a nested object, it will flatten the key=value pairs."
)
@click.argument("key")
@click.option("--export", is_flag=True, help="Include the export modified for each environment variable.")
@click.pass_context
def envify(ctx, key, export):
    def handler(vault):
        value = vault.get(key)
        if isinstance(value, dict):
            for k, v in value.items():
                click.echo(f"{'export ' if export else ''}{k}={serialize(v)}")
        else:
            click.echo(f"{'export ' if export else ''}{key}={serialize(value)}")

    with_vault(ctx, handler)


@cli.command(
    help="Store a secret. If the secret already exists, it will be overwritten. For example: `secrets set foo bar`"
)
@click.argument("key")
@click.argument("value")
@click.pass_context
def set(ctx, key, value):
    def handler(vault):
        vault.set(key, value)
        vault.save()

    with_vault(ctx, handler)


@cli.command("del", help="Delete a secret. For example: `secrets del foo`")
@click.argument("key")
@click.pass_context
def delete(ctx, key):
    def handler(vault):
        vault.delete(key)
        vault.save()

    with_vault(ctx, handler)


@cli.command(help="Open the secrets vault in your configured $EDITOR.")
@click.pass_context
def edit(ctx):
    def handler(vault):
        vault.edit_secrets()

    with_vault(ctx, handler)


if __name__ == "__main__":
    cli()
