class DomainError(Exception):
    """Base domain error."""


class InvalidInputError(DomainError):
    pass


class StorageError(DomainError):
    pass


class BlastError(DomainError):
    pass


class TaxonomyError(DomainError):
    pass


class RepositoryError(DomainError):
    pass
