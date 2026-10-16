class DomainError(Exception):
    """Base class for every business rule violation."""


class InvalidQuantity(DomainError):
    pass


class InsufficientStock(DomainError):
    pass


class InvalidTransition(DomainError):
    pass


class NotFound(DomainError):
    pass


class AlreadyExists(DomainError):
    pass
