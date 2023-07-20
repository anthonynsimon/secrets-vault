import argparse
import logging

from secrets_vault import SecretsVault, exceptions, constants


def main():
    parser = argparse.ArgumentParser(
        description="Encrypt and decrypt a local secrets file using a master.key"
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "-s",
        "--secrets-filepath",
        help=f"The location of the secrets file (default: {constants.DEFAULT_SECRETS_FILEPATH})",
    )
    parser.add_argument(
        "-m",
        "--master-key-filepath",
        help=f"The location of the master.key file (default: {constants.DEFAULT_MASTER_KEY_FILEPATH})",
    )
    parser.add_argument(
        "command", choices=["init", "get", "edit"], help="Command to run"
    )
    parser.add_argument(
        "key",
        nargs="?",
        help="When using the 'get' command, you can optionally provide a key to retrieve a specific item",
    )

    args = parser.parse_args()

    kwargs = {
        "secrets_filepath": args.secrets_filepath or constants.DEFAULT_SECRETS_FILEPATH,
        "master_key_filepath": args.master_key_filepath
        or constants.DEFAULT_MASTER_KEY_FILEPATH,
    }

    logging.basicConfig(level=logging.INFO if args.verbose else logging.ERROR)

    if args.command == "init":
        try:
            vault, master_key = SecretsVault.init()
            print(
                f"Generated new encryption master key:\n\n{master_key}\n\nKeep it safe! It will not be shown again."
            )
        except exceptions.SecretsFileAlreadyExists:
            print("Secrets file already exists, skipping init")
    elif args.command == "edit":
        try:
            SecretsVault(**kwargs).edit_secrets()
        except exceptions.MasterKeyNotFound:
            print(
                f"No master key found. Set it via the environment variable 'MASTER_KEY', or in a file at '{args.master_key_filepath}'"
            )
    elif args.command == "get":
        try:
            vault = SecretsVault(**kwargs)
            if args.key:
                print(vault.get(args.key))
            else:
                for key, value in vault.secrets.items():
                    print(f"{key}: {value}")
        except exceptions.MasterKeyNotFound:
            print(
                f"No master key found. Set it via the environment variable 'MASTER_KEY', or in a file at '{args.master_key_filepath}'"
            )
    else:
        raise NotImplementedError(f"Unknown command {args.command}")


if __name__ == "__main__":
    main()
