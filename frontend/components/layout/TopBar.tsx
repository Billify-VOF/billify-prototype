import React, { useState } from 'react';
import NotificationBell from '@/components/NotificationBell';
import SearchComponent from '@/components/SearchComponent';
import SearchResultItem from '@/components/SearchResultItem';
import { SearchItemResult } from '@/components/types';
import { AlertCircle, LogOut } from "lucide-react";
import Image from 'next/image';
import avatar from '../../assets/images/avatar.png'
import { useAuth } from '@/lib/auth/AuthContext';

const name = "H.Sophia";
const role = "Admin"

interface TopBarProps {
    onSearch: (query: string) => void;
    searchResult: SearchItemResult[];
}

const TopBar = ({ onSearch, searchResult }: TopBarProps) => {
    const [isProfileOpen, setIsProfileOpen] = useState(false);
    const { logout } = useAuth();

    const handleLogout = async () => {
        try {
            await logout();
        } catch (error) {
            console.error('Failed to logout:', error);
        }
    };

    return (
        <div className="bg-white border-b-2 border-gray-200 h-20 flex items-center justify-between px-5">
            <SearchComponent
                onSearch={onSearch}
                renderItem={(item) => (
                    <SearchResultItem item={item} onClick={() => { }} />
                )}
                results={searchResult}
            />

            <div className='flex flex-row gap-x-5 items-center w-full justify-end'>
                <AlertCircle size={20} className='cursor-pointer text-gray-500' />
                <NotificationBell />
                <div className='relative'>
                    <div 
                        className='flex flex-row items-center gap-x-3 cursor-pointer'
                        onClick={() => setIsProfileOpen(!isProfileOpen)}
                    >
                        <Image 
                            src={avatar} 
                            alt="User Avatar" 
                            width={40} 
                            height={40} 
                            className="rounded-full"
                        />
                        <div className='flex flex-col'>
                            <span className='font-semibold'>{name}</span>
                            <span className='text-gray-500'>{role}</span>
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
