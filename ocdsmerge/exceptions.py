class OCDSMergeError(Exception):
    """Base class for exceptions from within this package."""


class MissingDateKeyError(OCDSMergeError, KeyError):
    """Raised when a release is missing a 'date' key."""

    def __init__(self, key: str, message: str):
        self.key = key
        self.message = message

    def __str__(self) -> str:
        return str(self.message)


class NonObjectReleaseError(OCDSMergeError, TypeError):
    """Raised when a release is not an object."""


class NullDateValueError(OCDSMergeError, TypeError):
    """Raised when a release has a null 'date' value."""


class NonStringDateValueError(OCDSMergeError, TypeError):
    """Raised when a release has a non-string 'date' value."""


class InconsistentTypeError(OCDSMergeError, TypeError):
    """Raised when a path is a literal, an object, and/or an array in different releases."""


class OCDSMergeWarning(UserWarning):
    """Base class for warnings from within this package."""


class DuplicateIdValueWarning(OCDSMergeWarning):
    """Used when at least two objects in the same array have the same value for the 'id' field."""
