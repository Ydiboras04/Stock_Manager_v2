from enum import StrEnum


class Role(StrEnum):
    """The two BPMN actors who use the application."""

    STOCK_MANAGER = "STOCK_MANAGER"
    PURCHASING_MANAGER = "PURCHASING_MANAGER"
