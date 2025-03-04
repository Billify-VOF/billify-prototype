"""Domain model representing a notification and its business rules."""

from typing import Optional
from domain.models.value_objects import NotificationType
from domain.exceptions import InvalidNotificationError


class Notification:
    """
    Represents a notification in our system's domain model.
    
    Notifications are messages about events or actions within the system
    that need to be communicated to users.
    
    This is a pure domain model focused on business rules and behavior,
    without infrastructure or application-specific concerns.
    
    Attributes:
        message (str): The notification content
        type (NotificationType): The type/severity of notification
        is_read (bool): Whether the notification has been read
        related_entity (Optional[str]): Description of what entity this notification relates to
    """
    
    @classmethod
    def create(
        cls,
        message: str,
        type: NotificationType,
        is_read: bool = False,
        related_entity: Optional[str] = None
    ) -> 'Notification':
        """Create a new validated Notification.
        
        Factory method that creates and validates a notification instance.
        Use this method instead of constructor for normal notification creation.
        
        Args:
            message: The notification content
            type: The severity/type of the notification
            is_read: Whether the notification has been read (defaults to False)
            related_entity: Description of what entity this notification relates to
        
        Returns:
            Notification: A validated notification instance
            
        Raises:
            InvalidNotificationError: If validation fails
        """
        # Create instance
        notification = cls(
            message=message,
            type=type,
            is_read=is_read,
            related_entity=related_entity
        )
        
        # Validate the instance
        notification.validate()
        
        # Return validated instance
        return notification
    
    def __init__(
        self,
        message: str,
        type: NotificationType,
        is_read: bool = False,
        related_entity: Optional[str] = None
    ):
        """Initialize a new Notification instance.
        
        Note: This constructor does minimal validation. For validated instance creation,
        use the create() factory method instead.
        
        Args:
            message: The notification content
            type: The severity/type of the notification
            is_read: Whether the notification has been read
            related_entity: Description of what entity this notification relates to
        """
        self.message = message
        self.type = type
        self.is_read = bool(is_read)
        self.related_entity = related_entity
    
    def validate(self) -> None:
        """Validate this notification against business rules.
        
        Runs all validation checks and raises an exception if any fail.
        
        Raises:
            InvalidNotificationError: If the notification is invalid
        """
        self.validate_message()
        self.validate_type()
    
    def validate_message(self) -> None:
        """Validate the notification message.
        
        Raises:
            InvalidNotificationError: If message is empty or invalid
        """
        if not self.message or not self.message.strip():
            raise InvalidNotificationError("Notification message cannot be empty")
    
    def validate_type(self) -> None:
        """Validate the notification type.
        
        Raises:
            InvalidNotificationError: If type is not a valid NotificationType
        """
        if not isinstance(self.type, NotificationType):
            raise InvalidNotificationError(f"Invalid notification type: {self.type}")
    
    def mark_as_read(self) -> None:
        """Mark this notification as read.
        
        This is a domain behavior that changes the read status.
        """
        self.is_read = True 