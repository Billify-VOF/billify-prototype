'use client';

import { useState, useEffect, useRef } from 'react';
import { Bell, CheckCircle, Circle } from 'lucide-react';

interface Notification {
  id: string;
  message: string;
  isRead: boolean;
}

export default function NotificationBell(props: { className?: string }) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Fetch Notifications (Simulating API)
  useEffect(() => {
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
      setNotifications(dummyNotifications);
      setUnreadCount(dummyNotifications.filter((n) => !n.isRead).length);
    }

    fetchNotifications();
  }, []);

  // Toggle Notification Dropdown
  const toggleDropdown = () => {
    setOpen((prev) => !prev);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Mark notification as read/unread
  const toggleRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, isRead: !n.isRead } : n))
    );
    setUnreadCount((prev) =>
      notifications.find((n) => n.id === id)?.isRead ? prev + 1 : prev - 1
    );
  };

  return (
    <div
      className={`relative ${props.className}`}
      ref={dropdownRef}>
      {/* Notification Bell with Counter */}
      <button
        onClick={toggleDropdown}
        className='relative pr-2 pt-2'>
        <Bell className='w-6 h-6 text-gray-700' />
        {unreadCount > 0 && (
          <span className='absolute -top-1 -right-1 bg-red-500 text-white text-xs w-5 h-5 flex items-center justify-center rounded-full'>
            {unreadCount}
          </span>
        )}
      </button>

      {/* Floating Notification Dropdown */}
      {open && (
        <div className='absolute right-0 mt-2 w-72 bg-white shadow-lg rounded-lg border z-50 max-h-60 overflow-y-auto'>
          <div className='p-3 border-b text-gray-700 font-semibold'>
            Notifications
          </div>
          {notifications.length === 0 ? (
            <p className='text-gray-500 text-center p-3'>No notifications</p>
          ) : (
            notifications.slice(0, 5).map((notification) => (
              <div
                key={notification.id}
                className={`flex items-center justify-between p-3 hover:bg-gray-100 cursor-pointer ${
                  notification.isRead
                    ? 'text-gray-500'
                    : 'text-black font-medium'
                }`}
                onClick={() => toggleRead(notification.id)}>
                <span>{notification.message}</span>
                {notification.isRead ? (
                  <CheckCircle className='w-4 h-4 text-green-500' />
                ) : (
                  <Circle className='w-4 h-4 text-gray-300' />
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
