'use client';

import { useState, useEffect, useRef } from 'react';
import { Bell, CheckCircle, Circle } from 'lucide-react';

/**
 * Notification interface
 * @interface Notification
 * @property {string} id - Unique identifier for the notification
 * @property {string} message - Message content of the notification
 * @property {boolean} isRead - Read status of the notification
 */
interface Notification {
  id: string;
  message: string;
  isRead: boolean;
}

/**
 * NotificationBell component props
 * @param {Object} props - Component properties
 * @param {string} [props.className] - Optional class name for styling
 */
export default function NotificationBell(props: { className?: string }) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Fetch Notifications (Simulating API)
  useEffect(() => {
    let isMounted = true;
    async function fetchNotifications() {
      const dummyNotifications: Notification[] = [
        { id: '1', message: 'Invoice #1023 has been generated', isRead: false },
        {
          id: '2',
          message: 'Payment received for Invoice #9876',
          isRead: false,
        },
        { id: '3', message: 'Invoice #5643 is overdue', isRead: true },
        {
          id: '4',
          message: 'Reminder: Invoice #4321 due in 3 days',
          isRead: true,
        },
        {
          id: '5',
          message: 'Refund processed for Invoice #7890',
          isRead: false,
        },
      ];
      if (isMounted) {
        setNotifications(dummyNotifications);
        setUnreadCount(dummyNotifications.filter((n) => !n.isRead).length);
      }
    }

    // TODO: Make API call to search for notifications
    fetchNotifications();

    return () => {
      isMounted = false;
    };
  }, []);

  // Toggle Notification Dropdown
  const toggleDropdown = () => {
    setOpen((prev) => !prev);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Mark notification as read/unread
  const toggleRead = (id: string) => {
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, isRead: !n.isRead } : n)));
    setUnreadCount((prev) =>
      notifications.find((n) => n.id === id)?.isRead ? prev + 1 : prev - 1,
    );
  };

  return (
    <div className={`relative ${props.className}`} ref={dropdownRef}>
      {/* Notification Bell with Counter */}
      <button onClick={toggleDropdown} className="relative pr-2 pt-2">
        <Bell className="h-5 w-5 text-gray-700" />
        {unreadCount > 0 && (
          <span className="absolute right-1 top-1 flex h-3 w-3 items-center justify-center rounded-full bg-red-500 text-xs text-white">
            {unreadCount}
          </span>
        )}
      </button>

      {/* Floating Notification Dropdown */}
      {open && (
        <div className="absolute right-0 z-50 mt-2 max-h-60 w-72 overflow-y-auto rounded-lg border bg-white shadow-lg">
          <div className="border-b p-3 font-semibold text-gray-700">Notifications</div>
          {notifications.length === 0 ? (
            <p className="p-3 text-center text-gray-500">No notifications</p>
          ) : (
            notifications.slice(0, 5).map((notification) => (
              <div
                key={notification.id}
                className={`flex cursor-pointer items-center justify-between p-3 hover:bg-gray-100 ${
                  notification.isRead ? 'text-gray-500' : 'font-medium text-black'
                }`}
                onClick={() => toggleRead(notification.id)}
              >
                <span>{notification.message}</span>
                {notification.isRead ? (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                ) : (
                  <Circle className="h-4 w-4 text-gray-300" />
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
