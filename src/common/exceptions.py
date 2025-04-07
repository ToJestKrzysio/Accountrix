# Persistence layer base exceptions


class RecordDoesNotExist(Exception):
    """Exception raised when a record does not exist in the database."""

    pass


class RecordCreateFailed(Exception):
    """Exception raised when a record could not be created."""

    pass


class RecordUpdateFailed(Exception):
    """Exception raised when a record could not be updated."""

    pass


class RecordAlreadyExists(Exception):
    """Exception raised when a record could not be deleted."""

    pass
