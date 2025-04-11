import React, { useState } from 'react';
import NotificationBell from '@/components/NotificationBell';
import SearchComponent from '@/components/SearchComponent';
import SearchResultItem from '@/components/SearchResultItem';
import { SearchItemResult } from '@/components/types';
import { AlertCircle, LogOut, User } from 'lucide-react';
import { useAuth } from '@/lib/auth/AuthContext';
import { getDisplayName } from '@/lib/utils/userUtils';

interface TopBarProps {
  onSearch: (query: string) => void;
  searchResult: SearchItemResult[];
}

const TopBar = ({ onSearch, searchResult }: TopBarProps) => {
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const { logout, user } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="flex h-20 items-center justify-between border-b-2 border-gray-200 bg-white px-5">
      <SearchComponent
        onSearch={onSearch}
        renderItem={(item) => <SearchResultItem item={item} onClick={() => {}} />}
        results={searchResult}
      />

      <div className="flex w-full flex-row items-center justify-end gap-x-5">
        <AlertCircle size={20} className="cursor-pointer text-gray-500" />
        <NotificationBell />
        <div className="relative">
          <div
            className="flex cursor-pointer flex-row items-center gap-x-3"
            onClick={() => setIsProfileOpen(!isProfileOpen)}
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-200">
              <User className="h-6 w-6 text-gray-500" />
            </div>
            <div className="flex flex-col">
              <span className="font-semibold">
                {getDisplayName(user)}
              </span>
            </div>
          </div>
          {isProfileOpen && (
            <div className="absolute right-0 z-10 mt-2 w-48 rounded-lg border bg-white py-2 shadow-lg">
              <div
                className="flex cursor-pointer items-center gap-x-2 px-4 py-2 text-sm text-red-600 hover:bg-gray-50"
                onClick={handleLogout}
              >
                <LogOut size={16} />
                <span>Log out</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TopBar;
