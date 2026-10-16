import pytest

from stock.core import errors


@pytest.mark.parametrize(
    "error",
    [
        errors.InvalidQuantity,
        errors.InsufficientStock,
        errors.InvalidTransition,
        errors.NotFound,
        errors.AlreadyExists,
    ],
)
def test_every_error_is_a_domain_error(error):
    assert issubclass(error, errors.DomainError)
