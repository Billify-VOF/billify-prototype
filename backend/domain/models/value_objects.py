"""
Module containing value objects for the domain model.

This module defines immutable value objects used in the Billify domain model.

Currently includes:

- UrgencyLevel: For calculating and representing invoice urgency based on
  due dates.
"""
from enum import Enum


class UrgencyLevel(Enum):
    """
    Value object representing the urgency level of an invoice
    based on its due date.

    Each urgency level has an associated color code and day range.
    """
    OVERDUE = ("#8B0000", (None, -1))
    CRITICAL = ("#FF0000", (0, 7))
    HIGH = ("#FFA500", (8, 14))
    MEDIUM = ("#FFD700", (15, 30))
    LOW = ("#008000", (31, None))

    @property
    def color_code(self) -> str:
        """
        Returns the hex color code associated with this urgency level.

        Returns:
        str: The hex color code (e.g., '#FF0000' for red)
        """
        return self.value[0]

    @property
    def day_range(self) -> tuple[int | None, int | None]:
        """
        Returns the day range tuple for this urgency level.

        Returns:
        tuple: A tuple of (min_days, max_days) where None represents no limit
        """
        return self.value[1]

    @classmethod
    def calculate_from_days(cls, days: int) -> 'UrgencyLevel':
        """
        Calculates the appropriate urgency level based on days until due.

        Returns:
        UrgencyLevel: The calculated urgency level based on the days
        """
        if days < 0:
            return cls.OVERDUE
        if 0 <= days <= 7:
            return cls.CRITICAL
        if 8 <= days <= 14:
            return cls.HIGH
        if 15 <= days <= 30:
            return cls.MEDIUM
        if days >= 31:
            return cls.LOW
        raise ValueError(f"Invalid days value: {days}")
