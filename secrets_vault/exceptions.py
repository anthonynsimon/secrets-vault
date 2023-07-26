class SecretsStoreException(Exception):
    pass


class MasterKeyNotFound(SecretsStoreException):
    pass


class MasterKeyInvalid(SecretsStoreException):
    pass


class SecretsFileNotFound(SecretsStoreException):
    pass


class SecretsFileAlreadyExists(SecretsStoreException):
    pass


class MalformedSecretsFile(SecretsStoreException):
    pass
