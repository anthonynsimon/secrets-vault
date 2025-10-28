# Changelog

## 0.4.0
- Drop support for Python 2.7
- Textwrap encrypted vault

## 0.3.0
- Support for Python 3.8 - 3.14
- Support latest cryptography lib version
- Migrate to uv for dev and packaging

## 0.2.8
- Fix envify int boolean values

## 0.2.7
- Fix roundtrip yaml wrapping lines

## 0.2.6
- Add support to provide a custom dotenv path to `envify` command, eg. `secrets envify staging -o .env.staging`

## 0.2.5
- Fix serialize boolean values as `0,1` in envify command

## 0.2.4
- Add `--output` option and `--raw` flag to `envify` command

## 0.2.3
- When using the edit command, only persist the vault if there were changes (incl. comments)

## 0.2.2
- Add support to envify entire vault

## 0.2.1
- Fix envify output so it can be used by dotenv or environs lib

## 0.2.0
- Add support for yaml encoded vault files (new default). To use the old json format, pass `--format json` to the CLI.

## 0.1.12
- Auto-delete any temp files created during edit command
- Add support for nested paths in get/set commands

## 0.1.11
- Fix editor mode
- Add --verbose flag
- Minor fixes and improvements

## 0.1.10
- Relax library constraints

## 0.1.9
- Breaking change: Change encryption backend to AES-256-GCM
- Add `--export` option to envify.
- Update docs

## 0.1.8
- Move common params before command

## 0.1.7
- Relax requirements constraints
- Minor CLI tool fixes

## 0.1.6
- Fix requirements not listed in package

## 0.1.5
- Add envify command
- Refactor CLI tool
- Breaking Python API changes: persist() has been renamed to save(), and init() has been renamed to create().

## 0.1.4
- Add del command

## 0.1.3
- Add set command

## 0.1.2
- Initial release
