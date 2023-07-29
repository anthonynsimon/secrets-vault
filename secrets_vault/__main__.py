import json
import logging
from io import BytesIO

import click
from ruamel.yaml import YAML

from secrets_vault import SecretsVault, exceptions, constants, __version__


def serialize(v, format="yaml"):
    assert format in {"yaml", "json", "dotenv"}

    if isinstance(v, bool) and format == "dotenv":
        return "1" if v else "0"
    if not v:
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return str(v)
    if format == "json":
        return json.dumps(v, indent=2, default=str, sort_keys=False)
    if format == "dotenv":
        # encode non-value objects as json for use in env vars
        return json.dumps(v, default=str, sort_keys=False)
    if format == "yaml":
        fout = BytesIO()
        yaml = YAML(typ="rt")
        yaml.dump(v, fout)
        result = fout.getvalue().decode()
        fout.close()
        return result.strip()
    raise NotImplementedError(f"Unsupported format: {format}")


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
    "-f",
    "--format",
    default=constants.DEFAULT_FILE_FORMAT,
    help="Format to use for the secrets vault.",
    type=click.Choice(["yaml", "json"]),
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
            secrets_filepath=ctx.obj["secrets_filepath"],
            master_key_filepath=ctx.obj["master_key_filepath"],
            file_format=ctx.obj["format"],
        )
        click.echo(f"Generated new secrets vault at {ctx.obj['secrets_filepath']}")
        click.echo(f"Generated new master key at {ctx.obj['master_key_filepath']} - keep it safe!")
    except exceptions.SecretsFileAlreadyExists:
        print("Secrets file already exists, aborting...")
        exit(1)


def with_vault(ctx, func):
    try:
        vault = SecretsVault(
            secrets_filepath=ctx.obj["secrets_filepath"],
            master_key_filepath=ctx.obj["master_key_filepath"],
            file_format=ctx.obj["format"],
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


@cli.command(help="Get a secret value. If no specific key is provided, all secrets are printed.")
@click.argument("key", required=False)
@click.pass_context
def get(ctx, key):
    fformat = ctx.obj["format"]

    def handler(vault):
        if key:
            result = vault.get(key, default="")
        else:
            result = vault.secrets

        click.echo(serialize(result, fformat))

    with_vault(ctx, handler)


@cli.command(
    help="Prints a secret as an environment variable (eg. KEY=value). If no specific key is provided, all secrets are printed."
)
@click.argument("key", required=False)
@click.option("-e", "--export", is_flag=True, help="Include the export modifier for each environment variable.")
@click.option(
    "-o",
    "--output",
    type=click.Choice(["dotenv", "stdout"]),
    default="stdout",
    help="Output the result in the specified format.",
)
@click.option("--raw", is_flag=True, help="When raw mode is enabled, the key=value is printed as stored on the vault.")
@click.pass_context
def envify(ctx, key, export, output, raw):
    def serialize_key(k):
        return k if raw else k.upper().replace("-", "_")

    def write(obj):
        serialized = [
            f"{'export ' if export else ''}{serialize_key(k)}={serialize(v, 'dotenv')}" for k, v in obj.items()
        ]
        if output == "dotenv":
            with open(".env", "w") as f:
                f.write("\n".join(serialized))
        elif output == "stdout":
            for line in serialized:
                click.echo(line)
        else:
            raise NotImplementedError(f"Unsupported output format: {output}")

    def handler(vault):
        if key:
            value = vault.get(key)
            if isinstance(value, dict):
                write(value)
            else:
                write({key: value})
        else:
            write(vault.secrets)

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
