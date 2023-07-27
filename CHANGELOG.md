# Changelog

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