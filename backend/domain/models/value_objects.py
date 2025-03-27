"""Value objects for the Billify domain model.

This module defines immutable value objects that encapsulate business concepts
and their validation rules. Value objects are immutable and represent concepts
that are equal based on their properties rather than identity.

Currently includes:

- UrgencyLevel: Represents invoice urgency levels based on due dates
    - Used for visual indicators in the UI (colors)
    - Calculated from days until due date
    - Supports manual override for special cases

- InvoiceStatus: Represents the payment status of an invoice
    - Tracks if an invoice is pending, paid, or overdue
    - Used in both domain logic and persistence
    - Provides human-readable display names for UI

Usage:
    from domain.models.value_objects import UrgencyLevel, InvoiceStatus

    # Calculate urgency from days
    urgency = UrgencyLevel.calculate_from_days(days_until_due)

    # Get display name and color for UI
    display = urgency.display_name  # e.g., "Critical"
    color = urgency.color_code     # e.g., "#FF0000"

    # Use with Django models
    choices = UrgencyLevel.choices()  # For model field choices
"""
from enum import Enum
from typing import Optional


class UrgencyLevel(Enum):
    """Value object representing the urgency level of an invoice based on
    its due date.

    Each urgency level has an associated:
    - db_value: Integer value stored in database (e.g., 1)
    - color_code: Hex color for UI display (e.g., "#8B0000")
    - day_range: Tuple of (min_days, max_days) for calculation
      (e.g., (None, -1))
    - display_name: Auto-generated from enum name using title()
      (e.g., "Overdue")

    Naming Convention:
    - Enum members use UPPERCASE names with underscores for multiple words
    - Examples: OVERDUE, HIGH, VERY_HIGH, PAST_DUE
    - title() will convert underscores to spaces: PAST_DUE -> "Past Due"
    - This ensures display_name generates clean UI labels

    Example:
        level = UrgencyLevel.OVERDUE
        level.name == "OVERDUE"          # Enum member name
        level.db_value == 1              # Database value
        level.display_name == "Overdue"  # UI display value
        level.color_code == "#8B0000"    # UI color
        level.day_range == (None, -1)    # Calculation range
    """

    OVERDUE = (1, "#8B0000", (None, -1))
    CRITICAL = (2, "#FF0000", (0, 7))
    HIGH = (3, "#FFA500", (8, 14))
    MEDIUM = (4, "#FFD700", (15, 30))
    LOW = (5, "#008000", (31, None))

    # Type annotation for the value attribute of each enum member
    # (db_value, color_code, (min_days, max_days))
    value: tuple[int, str, tuple[Optional[int], Optional[int]]]

    @property
    def db_value(self) -> int:
        """Returns the database value associated with this urgency level.

        Returns:
            int: The database value
        """
        return self.value[0]

    @property
    def color_code(self) -> str:
        """Returns the hex color code associated with this urgency level.

        Returns:
            str: The hex color code (e.g., '#FF0000' for red)
        """
        return self.value[1]

    @property
    def day_range(self) -> tuple[Optional[int], Optional[int]]:
        """Returns the day range tuple for this urgency level.

        Returns:
            tuple: A tuple of (min_days, max_days) where None represents
                  no limit
        """
        return self.value[2]

    @property
    def display_name(self) -> str:
        """Returns a human-readable display name for the urgency level.

        Automatically converts the enum member name to a display name by:
        1. Taking the enum member name (e.g., "OVERDUE" or "PAST_DUE")
        2. Converting it to title case with spaces (e.g., "Overdue" or
           "Past Due")

        Note:
        - Enum members should use UPPERCASE with underscores for multiple words
        - Underscores are converted to spaces in the display name

        Examples:
            UrgencyLevel.OVERDUE.display_name == "Overdue"
            UrgencyLevel.HIGH.display_name == "High"
            # If we had multi-word names:
            # UrgencyLevel.PAST_DUE.display_name == "Past Due"
            # UrgencyLevel.VERY_HIGH.display_name == "Very High"

        Returns:
            str: The human-readable display name for this urgency level
        """
        return self.name.title()  # OVERDUE -> Overdue, PAST_DUE -> "Past Due"

    @classmethod
    def choices(cls) -> list[tuple[int, str]]:
        """Returns choices in Django format for form fields and model
        definitions.

        Creates a list of tuples where each tuple contains:
        - First element: db_value (int) - The value stored in database
        - Second element: display_name (str) - The human-readable label

        Example:
            UrgencyLevel.choices() returns:
            [
                (1, "Overdue"),
                (2, "Critical"),
                (3, "High"),
                (4, "Medium"),
                (5, "Low")
            ]

        Returns:
            list[tuple[int, str]]: List of (db_value, display_name) pairs
        """
        return [(urgency.db_value, urgency.display_name) for urgency in cls]

    @classmethod
    def calculate_from_days(cls, days: int) -> "UrgencyLevel":
        """Calculates the appropriate urgency level based on days until due.

        Maps the number of days until due (or overdue if negative) to an
        urgency level according to these rules:
        - OVERDUE:  days < 0 (past due date)
        - CRITICAL: 0-7 days until due
        - HIGH:     8-14 days until due
        - MEDIUM:   15-30 days until due
        - LOW:      31+ days until due

        Args:
            days (int): Number of days until due date
                       Negative values indicate overdue invoices
                       Positive values indicate days remaining

        Returns:
            UrgencyLevel: The calculated urgency level

        Raises:
            ValueError: If days is None or not a valid integer

        Examples:
            >>> UrgencyLevel.calculate_from_days(-5)
            UrgencyLevel.OVERDUE
            >>> UrgencyLevel.calculate_from_days(3)
            UrgencyLevel.CRITICAL
            >>> UrgencyLevel.calculate_from_days(40)
            UrgencyLevel.LOW
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

    @classmethod
    def from_db_value(cls, db_value: int) -> "UrgencyLevel":
        for level in UrgencyLevel:
            if db_value == level.db_value:
                return level
        raise ValueError(f"Invalid urgency db_value: {db_value}")


class InvoiceStatus(Enum):
    """Value object representing the payment status of an invoice.

    Provides status values and display names for invoice payment states.
    Used by both domain and infrastructure layers.

    Each enum member (e.g., PENDING, PAID, OVERDUE) has:
    - name: The enum member's name (e.g., "PENDING")
    - value: The string value stored in database (e.g., "pending")
    - display_name: Human-readable version for UI (e.g., "Pending Payment")

    Example:
        status = InvoiceStatus.PENDING
        status.name == "PENDING"           # Enum member name
        status.value == "pending"          # Database value
        status.display_name == "Pending Payment"  # UI display value
    """

    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"

    value: str  # This indicates each enum member has a string value

    @property
    def display_name(self) -> str:
        """Returns a human-readable display name for the invoice status.

        Uses a dictionary mapping to convert the enum's value (e.g., "pending")
        to its display form (e.g., "Pending Payment").

        The mapping is:
            "pending" -> "Pending Payment"
            "paid" -> "Payment Received"
            "overdue" -> "Payment Overdue"

        Technical Implementation:
        This property uses Python's dictionary lookup syntax (dict[key]) to map
        the enum's value to its display name. For example:
        - If self.value is "pending", dict["pending"] returns "Pending Payment"
        - If self.value is "paid", dict["paid"] returns "Payment Received"
        - If self.value is "overdue", dict["overdue"] returns "Payment Overdue"

        This is equivalent to writing:
            mapping = {
                'pending': 'Pending Payment',
                'paid': 'Payment Received',
                'overdue': 'Payment Overdue'
            }
            return mapping[self.value]

        Returns:
            str: The human-readable display name for this status
        """
        status_display_names = {
            "pending": "Pending Payment",
            "paid": "Payment Received",
            "overdue": "Payment Overdue",
        }
        return status_display_names.get(self.value, f"Unknown Status: {self.value}")

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        """Returns choices in Django format for form fields and model
        definitions.

        Creates a list of tuples where each tuple contains:
        - First element: value (str) - The value stored in database
        - Second element: display_name (str) - The human-readable label

        Example:
            InvoiceStatus.choices() returns:
            [
                ("pending", "Pending Payment"),
                ("paid", "Payment Received"),
                ("overdue", "Payment Overdue")
            ]

        Returns:
            list[tuple[str, str]]: List of (value, display_name) pairs
        """
        return [(status.value, status.display_name) for status in cls]

    @classmethod
    def from_db_value(cls, db_value: str) -> "InvoiceStatus":
        for status in InvoiceStatus:
            if db_value == status.value:
                return status
        raise ValueError(f"Invalid status db_value: {db_value}")
