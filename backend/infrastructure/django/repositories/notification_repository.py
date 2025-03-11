"""Django ORM implementation of the notification repository interface."""

from typing import Optional, List
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from domain.repositories.interfaces.notification_repository import NotificationRepository
from domain.models.notification import Notification as DomainNotification
from domain.models.value_objects import NotificationType
from infrastructure.django.models.notification import Notification as DjangoNotification

import logging

# Module-level logger
logger = logging.getLogger(__name__)


class DjangoNotificationRepository(NotificationRepository):
    """Django ORM implementation of the notification repository.
    
    This class bridges the domain model and Django ORM model for notifications,
    handling persistence operations while maintaining the domain model's integrity.
    
    It implements all methods defined in the NotificationRepository interface,
    translating between domain and database representations as needed.
    """

    def _to_domain(self, db_notification: DjangoNotification) -> DomainNotification:
        """Convert Django model to domain model.
        
        Args:
            db_notification: Django ORM notification model instance
            
        Returns:
            Domain notification object
        """
        logger.debug("Converting DB notification to domain model: %s", db_notification)
        
        # Get the related entity description if available
        related_entity = None
        if db_notification.content_type and db_notification.object_id:
            # Using getattr for safer access to the model attribute
            model_name = getattr(db_notification.content_type, 'model', 'unknown')
            related_entity = f"{model_name}:{db_notification.object_id}"
            
        # Create the domain notification object
        domain_notification = DomainNotification.create(
            message=db_notification.message,
            type=NotificationType[db_notification.notification_type.upper()],
            is_read=db_notification.read_at is not None,
            related_entity=related_entity
        )
        
        return domain_notification 

    def save(self, notification: DomainNotification, user_id: int) -> DomainNotification:
        """Persist a notification to storage.

        Args:
            notification: Domain model to be saved
            user_id: ID of the user the notification is for

        Returns:
            DomainNotification: The saved domain model with any updates
        """
        logger.debug("Saving notification for user %d: %s", user_id, notification.message)
        
        # Parse related entity if provided
        content_type = None
        object_id = None
        
        if notification.related_entity:
            try:
                # Expected format: "model_name:id"
                parts = notification.related_entity.split(":")
                if len(parts) == 2:
                    model_name, object_id = parts
                    content_type = ContentType.objects.get(model=model_name)
                    object_id = int(object_id)
            except (ValueError, ObjectDoesNotExist) as e:
                logger.warning("Could not parse related entity %s: %s", 
                              notification.related_entity, str(e))
        
        # Create and save the Django notification
        db_notification = DjangoNotification(
            user_id=user_id,
            message=notification.message,
            notification_type=notification.type.db_value,
        )
        
        # Set content type and object ID if available
        if content_type and object_id:
            db_notification.content_type = content_type
            db_notification.object_id = object_id
        
        # Set read status if already read
        if notification.is_read:
            db_notification.read_at = timezone.now()
        
        # Save to database
        db_notification.save()
        
        # Return the domain model (with any updates if needed)
        return notification 

    def get_by_id(self, notification_id: int) -> Optional[DomainNotification]:
        """Retrieve a notification by its ID.
        
        Args:
            notification_id: The unique identifier of the notification
            
        Returns:
            Optional[DomainNotification]: The notification if found, None otherwise
        """
        try:
            db_notification = DjangoNotification.objects.get(id=notification_id)
            return self._to_domain(db_notification)
        except DjangoNotification.DoesNotExist:
            logger.debug("Notification with ID %d not found", notification_id)
            return None 

    def get_for_user(self, user_id: int) -> List[DomainNotification]:
        """Get all notifications for a specific user.
        
        Args:
            user_id: ID of the user whose notifications to retrieve
            
        Returns:
            List[DomainNotification]: List of notification domain objects
        """
        db_notifications = DjangoNotification.objects.filter(user_id=user_id)
        
        if not db_notifications.exists():
            logger.debug("No notifications found for user %d", user_id)
            return []
        
        return [self._to_domain(n) for n in db_notifications] 

    def get_unread_for_user(self, user_id: int) -> List[DomainNotification]:
        """Get unread notifications for a specific user.
        
        Args:
            user_id: ID of the user whose unread notifications to retrieve
            
        Returns:
            List[DomainNotification]: List of unread notification domain objects
        """
        db_notifications = DjangoNotification.objects.filter(
            user_id=user_id, 
            read_at__isnull=True
        )
        
        if not db_notifications.exists():
            logger.debug("No unread notifications found for user %d", user_id)
            return []
        
        return [self._to_domain(n) for n in db_notifications] 

    def get_by_type_for_user(self, user_id: int, notification_type: NotificationType) -> List[DomainNotification]:
        """Get notifications of a specific type for a user.
        
        Args:
            user_id: ID of the user whose notifications to retrieve
            notification_type: The type of notifications to retrieve
            
        Returns:
            List[DomainNotification]: List of notifications of the specified type
        """
        db_notifications = DjangoNotification.objects.filter(
            user_id=user_id,
            notification_type=notification_type.db_value
        )
        
        if not db_notifications.exists():
            logger.debug("No notifications of type %s found for user %d", 
                        notification_type.db_value, user_id)
            return []
        
        return [self._to_domain(n) for n in db_notifications] 

    def mark_as_read(self, notification_id: int) -> DomainNotification:
        """Mark a notification as read.
        
        Args:
            notification_id: The unique identifier of the notification to mark as read
            
        Returns:
            DomainNotification: The updated notification domain object
            
        Raises:
            ValueError: If the notification with the specified ID is not found
        """
        try:
            db_notification = DjangoNotification.objects.get(id=notification_id)
            db_notification.mark_as_read()
            return self._to_domain(db_notification)
        except DjangoNotification.DoesNotExist:
            logger.warning("Attempted to mark non-existent notification as read: %d", notification_id)
            raise ValueError(f"Notification with ID {notification_id} not found") 