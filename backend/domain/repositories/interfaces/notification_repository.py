"""Notification repository interface for data access operations.

This module defines the abstract interface for notification data access operations
using Python's ABC (Abstract Base Class). The interface serves as a contract
that all concrete repository implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from backend.domain.models.notification import Notification
from backend.domain.models.value_objects import NotificationType


class NotificationRepository(ABC):
    """Interface defining notification data access operations.

    This abstract base class serves as a contract for notification persistence
    operations. Any concrete implementation (e.g., Django ORM, SQLAlchemy,
    etc.) must implement all methods marked with @abstractmethod.
    
    Methods are designed to reflect domain language and concepts rather than
    technical filtering parameters.
    """
    
    @abstractmethod
    def save(self, notification: Notification, user_id: int) -> Notification:
        """Persist a notification to storage.

        Args:
            notification: Domain model to be saved
            user_id: ID of the user the notification is for

        Returns:
            Notification: The saved domain model with any
                updates (like assigned ID)
        """
        pass

    @abstractmethod
    def get_by_id(self, notification_id: int) -> Optional[Notification]:
        """Retrieve a notification by its ID.
        
        Args:
            notification_id: The unique identifier of the notification
            
        Returns:
            Optional[Notification]: The notification if found, None otherwise
        """
        pass

    @abstractmethod
    def get_for_user(self, user_id: int) -> List[Notification]:
        """Get all notifications for a specific user.
        
        Args:
            user_id: ID of the user whose notifications to retrieve
            
        Returns:
            List[Notification]: List of notification domain objects
        """
        pass
        
    @abstractmethod
    def get_unread_for_user(self, user_id: int) -> List[Notification]:
        """Get unread notifications for a specific user.
        
        Args:
            user_id: ID of the user whose unread notifications to retrieve
            
        Returns:
            List[Notification]: List of unread notification domain objects
        """
        pass
        
    @abstractmethod
    def get_by_type_for_user(self, user_id: int, notification_type: NotificationType) -> List[Notification]:
        """Get notifications of a specific type for a user.
        
        Args:
            user_id: ID of the user whose notifications to retrieve
            notification_type: The type of notifications to retrieve
            
        Returns:
            List[Notification]: List of notifications of the specified type
        """
        pass
        
    @abstractmethod
    def mark_as_read(self, notification_id: int) -> Notification:
        """Mark a notification as read.
        
        Args:
            notification_id: The unique identifier of the notification to mark as read
            
        Returns:
            Notification: The updated notification domain object
        """
        pass 