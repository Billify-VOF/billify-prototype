"""Django ORM model for notification persistence and database operations."""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from typing import Optional

from domain.models.value_objects import NotificationType

# Module-level logger
logger = logging.getLogger(__name__)


class Notification(models.Model):
    """Database model for storing user notifications.

    This model handles the persistence of notification data in the database.
    It focuses on data integrity and storage, while business logic
    is handled in the domain model.

    Attributes:
        id (AutoField): Primary key, automatically added by Django.
                     Auto-incrementing integer field that uniquely
                     identifies each notification.
        user (ForeignKey): User who should receive the notification
        message (TextField): The notification message text
        type (CharField): The type/severity of the notification (info, warning, error)
        created_at (DateTimeField): When the notification was created
        read_at (DateTimeField): When the notification was read (null if unread)
        content_type (ForeignKey): Type of the related object (ContentType)
        object_id (PositiveIntegerField): ID of the related object
        content_object (GenericForeignKey): The related object instance

    Key Assumptions:
        - All notifications are associated with a specific user
        - Notifications can be marked as read but not deleted
        - Notifications may optionally relate to another object in the system
        - Timestamps are automatically managed
    """

    objects = models.Manager()
    
    # Core notification data
    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="User who should receive this notification"
    )
    
    message: models.TextField = models.TextField(
        help_text="The notification message content"
    )
    
    type: models.CharField = models.CharField(
        max_length=20,
        choices=[(t.db_value, t.display_name) for t in NotificationType],
        default=NotificationType.INFO.db_value,
        help_text="Type/severity of the notification (info, warning, error)"
    )
    
    # Timestamps
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        help_text="When the notification was created"
    )
    
    read_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the notification was read (null if unread)"
    )
    
    # Generic foreign key implementation (replaces the custom related_object fields)
    content_type: models.ForeignKey = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Type of the related object (e.g., Invoice model, User model)"
    )
    
    object_id: models.PositiveIntegerField = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID of the related object"
    )
    
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        """Model metadata options.
        
        Controls ordering, indexes, constraints, table name, and other metadata.
        """
        # Order by created_at in descending order (newest first)
        ordering = ['-created_at']
        
        # Human-readable names for admin interface and documentation
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        
        # Database indexes for frequently queried fields
        indexes = [
            models.Index(fields=['user', '-created_at'], name='notif_user_date_idx'),
            models.Index(fields=['user', 'read_at'], name='notif_user_read_idx'),
            models.Index(fields=['content_type', 'object_id'], name='notif_content_idx'),
        ]
    
    def __init__(self, *args, **kwargs):
        """Initialize notification instance with additional setup.
        
        Performs any necessary conversions or initializations when
        a new instance is created, either from the database or in code.
        
        This method is called both when creating new objects and when
        loading existing objects from the database.
        """
        super().__init__(*args, **kwargs)
        
        # Initialize any instance attributes that aren't directly 
        # mapped to database fields (if needed in the future)
        
        # Pre-process any values that need conversion before use
        # For now, we don't need any special initialization logic,
        # but the structure is in place for future extensions
    
    def __str__(self) -> str:
        """Return a string representation of the notification.
        
        Format: "[TYPE] Message (for username) [Read/Unread]"
        This is used in the Django admin, debugging, and logging.
        
        Returns:
            String representation of the notification.
        """
        status = "Read" if self.is_read else "Unread"
        # Truncate message if too long
        short_message = (self.message[:40] + '...') if len(self.message) > 40 else self.message
        
        # Use NotificationType enum to get display name
        # Django automatically generates get_FOO_display for choice fields
        type_display = self.get_type_display()  # type: ignore
        
        # Access username safely
        username = getattr(self.user, 'username', 'unknown')
        
        return f"[{type_display}] {short_message} (for {username}) [{status}]"
    
    @classmethod
    def create(
        cls,
        message: str,
        type_value: str,
        user_id: int,
        content_type_id: Optional[int] = None,
        object_id: Optional[int] = None,
        is_read: bool = False
    ) -> 'Notification':
        """Create a new notification with validation.
        
        Factory method that encapsulates creation logic and ensures
        proper validation before saving to the database.
        
        Args:
            message: The notification message content
            type_value: The notification type (must be a valid NotificationType db_value)
            user_id: ID of the user who should receive this notification
            content_type_id: Optional ContentType ID for related object
            object_id: Optional ID of related object
            is_read: Whether notification is already read (default: False)
            
        Returns:
            Notification: The created and saved notification instance
            
        Raises:
            ValidationError: If validation fails for any field
        """
        # Create notification instance
        notification = cls(
            message=message,
            type=type_value,
            user_id=user_id
        )
        
        # Set optional fields if provided
        if content_type_id is not None and object_id is not None:
            notification.content_type_id = content_type_id
            notification.object_id = object_id
            
        # Set read status if notification is already read
        if is_read:
            notification.read_at = timezone.now()
        
        # Validate and save
        notification.full_clean()
        notification.save()
        
        return notification
    
    def clean(self) -> None:
        """Validate notification data before saving.
        
        Calls specialized validation methods for each field requiring custom validation.
        
        Raises:
            ValidationError: If any validation checks fail
        """
        super().clean()
        self._validate_message()
        self._validate_type()
    
    def _validate_message(self) -> None:
        """Validate the notification message.
        
        Ensures the message is not empty or just whitespace.
        
        Raises:
            ValidationError: If message is empty or only contains whitespace
        """
        if not self.message or not self.message.strip():
            raise ValidationError({
                'message': 'Notification message cannot be empty.'
            })
    
    def _validate_type(self) -> None:
        """Validate the notification type.
        
        Ensures the type is one of the valid types defined in NotificationType.
        
        Raises:
            ValidationError: If type is not a valid NotificationType value
        """
        valid_types = [t.db_value for t in NotificationType]
        if self.type not in valid_types:
            raise ValidationError({
                'type': f'Invalid notification type. Must be one of: {", ".join(valid_types)}'
            })
    
    def update(
        self,
        *,
        message: Optional[str] = None,
        type_value: Optional[str] = None,
        content_type_id: Optional[int] = None,
        object_id: Optional[int] = None,
        mark_read: Optional[bool] = None
    ) -> 'Notification':
        """Update notification fields with validation.
        
        Encapsulates updates to notification fields, ensuring proper validation
        is performed before saving changes.
        
        Args:
            message: New notification message
            type_value: New notification type value
            content_type_id: New content type ID for related object
            object_id: New object ID for related object
            mark_read: If True, marks notification as read
            
        Returns:
            Notification: The updated notification instance (self)
            
        Raises:
            ValidationError: If updated fields don't meet validation requirements
        """
        # Update fields if provided
        if message is not None:
            self.message = message
            
        if type_value is not None:
            self.type = type_value
            
        # Handle related object fields together
        if content_type_id is not None:
            self.content_type_id = content_type_id
            
        if object_id is not None:
            self.object_id = object_id
            
        # Handle read status
        if mark_read is True and not self.is_read:
            self.read_at = timezone.now()
        elif mark_read is False and self.is_read:
            self.read_at = None
        
        # Validate all fields
        self.full_clean()
        
        # Save changes
        self.save()
        
        return self
    
    def mark_as_read(self) -> 'Notification':
        """Mark the notification as read with the current timestamp.
        
        If the notification is already read, this is a no-op.
        
        Returns:
            The notification instance (self) for method chaining.
        """
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])
        return self
    
    @property
    def is_read(self) -> bool:
        """Check if the notification has been read.
        
        Returns:
            True if the notification has been read, False otherwise.
        """
        return self.read_at is not None
    
    # Following YANGI (You Ain't Gonna Need It) principles, we're intentionally keeping
    # this model focused on core functionality. Additional methods like custom managers,
    # bulk operations, or advanced filtering will be added only when specific use cases
    # emerge from actual application usage. This prevents premature optimization and
    # unnecessary complexity while maintaining a clean, maintainable codebase that
    # evolves based on real requirements. 