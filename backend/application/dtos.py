"""Data Transfer Objects (DTOs) for the application layer.

DTOs are simple data containers used to transfer data between different
layers of the application. They help decouple the domain model from
client-facing interfaces and use cases.

Unlike domain objects, DTOs:
- Have no behavior (only data)
- Are not bound by domain rules
- Can be tailored to specific use cases
- May flatten or combine data from multiple domain objects
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from backend.domain.models.value_objects import NotificationType


@dataclass
class NotificationFilterParameters:
    """Parameters for filtering notifications in application use cases.
    
    This DTO represents query parameters for notification filtering,
    separating infrastructure concerns from domain logic.
    
    All fields are optional to allow filtering on any combination of attributes.
    
    Attributes:
        read: When provided, filters by the read status of notifications
              True = only read notifications, False = only unread notifications
        notification_type: When provided, filters to only notifications of this type
        created_after: When provided, only includes notifications created after this datetime
        created_before: When provided, only includes notifications created before this datetime
    """
    read: Optional[bool] = None
    notification_type: Optional[NotificationType] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None 