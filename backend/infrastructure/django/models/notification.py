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
        notification_type (CharField): The type/severity of the notification (info, warning, error)
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
    
    notification_type: models.CharField = models.CharField(
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
        logger.debug("Django Notification __init__ called")
        logger.debug("Number of args: %s", len(args))
        for i, arg in enumerate(args):
            logger.debug("arg[%s]: %s (type: %s)", i, arg, type(arg))
        logger.debug("kwargs: %s", kwargs)
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
        type_display = self.get_notification_type_display()  # type: ignore
        
        # Access username safely
        username = getattr(self.user, 'username', 'unknown')
        
        return f"[{type_display}] {short_message} (for {username}) [{status}]"
    
    @classmethod
    def create(
        cls,
        message: str,
        notification_type_value: str,
        user_id: int,
        content_type_id: Optional[int] = None,
        object_id: Optional[int] = None,
        is_read: bool = False
    ) -> 'Notification':
        """Create a new notification database record.
        
        Factory method that focuses on database persistence with necessary constraint validation.
        While business rules should be validated at the domain layer, this method ensures
        database constraints are satisfied before persisting.
        
        Args:
            message: The notification message content
            notification_type_value: The notification type (must be a valid NotificationType db_value)
            user_id: ID of the user who should receive this notification
            content_type_id: Optional ContentType ID for related object
            object_id: Optional ID of related object
            is_read: Whether notification is already read (default: False)
            
        Returns:
            Notification: The created and saved notification instance
            
        Raises:
            ValidationError: If database constraints are violated
        """
        logger.info("Creating notification for user_id=%s, notification_type=%s", user_id, notification_type_value)
        
        # Create notification instance
        notification = cls(
            message=message,
            notification_type=notification_type_value,
            user_id=user_id
        )
        
        # Set optional fields if provided
        if content_type_id is not None and object_id is not None:
            logger.debug("Setting related object: content_type_id=%s, object_id=%s", 
                        content_type_id, object_id)
            notification.content_type_id = content_type_id
            notification.object_id = object_id
            
        # Set read status if notification is already read
        if is_read:
            logger.debug("Marking notification as read on creation")
            notification.read_at = timezone.now()
        
        # Validate database constraints 
        notification.full_clean()
        
        # Save to database
        notification.save()
        
        return notification
    
    def clean(self) -> None:
        """Validate database integrity constraints.
        
        This validation focuses on ensuring database integrity rather than
        business rules, which should be handled at the domain layer.
        
        Raises:
            ValidationError: If database constraints are violated
        """
        logger.debug("Validating notification database constraints: id=%s, user_id=%s", 
                   getattr(self, 'id', 'new'), getattr(self, 'user_id', None))
        super().clean()
        self._validate_message()
        self._validate_notification_type()
    
    def _validate_message(self) -> None:
        """Validate the notification message meets database requirements.
        
        Ensures the message field satisfies basic requirements for database persistence.
        For full business rule validation, use the domain model.
        
        Raises:
            ValidationError: If message is empty or only contains whitespace
        """
        logger.debug("Validating message field: '%s'", 
                   self.message[:30] + '...' if self.message and len(self.message) > 30 else self.message)
        if not self.message or not self.message.strip():
            logger.warning("Validation failed: Empty notification message")
            raise ValidationError({
                'message': 'Notification message cannot be empty.'
            })
    
    def _validate_notification_type(self) -> None:
        """Validate the notification type meets database requirements.
        
        Ensures the notification_type value is one of the valid options defined in the choices.
        This is primarily for database integrity rather than business rule validation.
        
        Raises:
            ValidationError: If notification_type is not a valid choice value
        """
        logger.debug("Validating notification_type field: '%s'", self.notification_type)
        valid_types = [t.db_value for t in NotificationType]
        if self.notification_type not in valid_types:
            logger.warning("Validation failed: Invalid notification type '%s'", self.notification_type)
            raise ValidationError({
                'notification_type': f'Invalid notification type. Must be one of: {", ".join(valid_types)}'
            })
    
    def update(
        self,
        *,
        message: Optional[str] = None,
        notification_type_value: Optional[str] = None,
        content_type_id: Optional[int] = None,
        object_id: Optional[int] = None,
        mark_read: Optional[bool] = None
    ) -> 'Notification':
        """Update notification fields with database constraint validation.
        
        Updates notification fields and ensures database integrity constraints
        are satisfied. Business rules should be validated at the domain layer
        before calling this method.
        
        Args:
            message: New notification message
            notification_type_value: New notification type value
            content_type_id: New content type ID for related object
            object_id: New object ID for related object
            mark_read: If True, marks notification as read
            
        Returns:
            Notification: The updated notification instance (self)
            
        Raises:
            ValidationError: If database constraints are violated
        """
        logger.info("Updating notification id=%s for user_id=%s", 
                  self.id, getattr(self, 'user_id', None))
        
        # Update fields if provided
        if message is not None:
            logger.debug("Updating message from '%s' to '%s'", 
                       self.message[:30] + '...' if len(self.message) > 30 else self.message,
                       message[:30] + '...' if len(message) > 30 else message)
            self.message = message
            
        if notification_type_value is not None:
            logger.debug("Updating notification type from '%s' to '%s'", self.notification_type, notification_type_value)
            self.notification_type = notification_type_value
            
        # Handle related object fields together
        if content_type_id is not None:
            logger.debug("Updating content_type_id from %s to %s", self.content_type_id, content_type_id)
            self.content_type_id = content_type_id
            
        if object_id is not None:
            logger.debug("Updating object_id from %s to %s", self.object_id, object_id)
            self.object_id = object_id
            
        # Handle read status
        if mark_read is True and not self.is_read:
            logger.debug("Marking notification as read")
            self.read_at = timezone.now()
        elif mark_read is False and self.is_read:
            logger.debug("Marking notification as unread")
            self.read_at = None
        
        # Validate database constraints
        self.full_clean()
        
        # Save changes
        self.save()
        logger.debug("Notification updated successfully")
        
        return self
    
    def mark_as_read(self) -> 'Notification':
        """Mark the notification as read with the current timestamp.
        
        If the notification is already read, this is a no-op.
        
        Returns:
            The notification instance (self) for method chaining.
        """
        if not self.read_at:
            logger.info("Marking notification id=%s as read", self.id)
            self.read_at = timezone.now()
            self.save()
        else:
            logger.debug("Notification id=%s already marked as read", self.id)
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