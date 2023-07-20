import argparse
import logging

from secrets_vault import SecretsVault, exceptions, constants


def secrets_key_already_exists():
    print("Secrets file already exists, skipping init")
    exit(1)


def no_master_key():
    print(
        f"No master key found. Set it via the environment variable 'MASTER_KEY', or in a file at '{args.master_key_filepath}'"
    )
    exit(1)


def main():
    parser = argparse.ArgumentParser(description="Encrypt and decrypt a local secrets file using a master.key")

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
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
    parser.add_argument("command", choices=["init", "get", "set", "del", "edit"], help="Command to run")
    parser.add_argument(
        "key",
        nargs="?",
    )
    parser.add_argument(
        "value",
        nargs="?",
    )

    args = parser.parse_args()

    kwargs = {
        "secrets_filepath": args.secrets_filepath or constants.DEFAULT_SECRETS_FILEPATH,
        "master_key_filepath": args.master_key_filepath or constants.DEFAULT_MASTER_KEY_FILEPATH,
    }

    logging.basicConfig(level=logging.INFO if args.verbose else logging.ERROR)

    if args.command == "init":
        try:
            vault, master_key = SecretsVault.init()
            print(f"Generated new encryption master key:\n\n{master_key}\n\nKeep it safe! It will not be shown again.")
        except exceptions.SecretsFileAlreadyExists:
            secrets_key_already_exists()
    elif args.command == "edit":
        try:
            SecretsVault(**kwargs).edit_secrets()
        except exceptions.MasterKeyNotFound:
            no_master_key()
    elif args.command == "get":
        try:
            vault = SecretsVault(**kwargs)
            if args.key:
                print(vault.get(args.key))
            else:
                for key, value in vault.secrets.items():
                    print(f"{key}: {value}")
        except exceptions.MasterKeyNotFound:
            no_master_key()
    elif args.command == "set":
        (args.key and args.value) or parser.error("key and value are required")
        try:
            vault = SecretsVault(**kwargs)
            vault.set(args.key, args.value)
            vault.persist()
            no_master_key()
        except exceptions.MasterKeyNotFound:
            no_master_key()
    elif args.command == "del":
        args.key or parser.error("key is required")
        try:
            vault = SecretsVault(**kwargs)
            vault.delete(args.key)
            vault.persist()
        except exceptions.MasterKeyNotFound:
            no_master_key()
    else:
        print(f"Unknown command {args.command}")
        exit(1)


if __name__ == "__main__":
    main()
