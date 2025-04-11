import React from 'react';
import NotificationBell from '@/components/NotificationBell';
import SearchComponent from '@/components/SearchComponent';
import SearchResultItem from '@/components/SearchResultItem';
import { SearchItemResult } from '@/components/types';
import { AlertCircle } from "lucide-react";
import avatar from '../../../assets/images/avatar.png'

const name = "H.Sophia";
const role = "Admin"

interface TopBarProps {
    onSearch: (query: string) => void;
    searchResult: SearchItemResult[];
}

const TopBar = ({ onSearch, searchResult }: TopBarProps) => {
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
                <div className='flex flex-row items-center gap-x-3 cursor-pointer'>
                    <img src={avatar.src} alt="avatar">
                    </img>
                    <div className='flex flex-col'>
                        <span className='font-semibold'>{name}</span>
                        <span className='text-gray-500'>{role}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TopBar;
