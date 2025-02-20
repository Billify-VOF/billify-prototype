'use client';

import { useEffect, useRef, useState } from 'react';
// import { Input } from "@/components/ui/input";
import { Card, CardContent } from '@/components/ui/card';
import { Loader2, Search, AlertCircle } from 'lucide-react';
import { set } from 'date-fns';

interface SearchComponentProps<T> {
  onSearch: (query: string) => Promise<void>;
  renderItem: (item: T) => React.ReactNode;
  results: T[];
}

export default function SearchComponent<T>({
  onSearch,
  renderItem,
  results,
}: SearchComponentProps<T>) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

    // Close dropdown when clicking outside
    useEffect(() => {
      function handleClickOutside(event: MouseEvent) {
        if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
          setShowDropdown(false);
        }
      }
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    useEffect(() => {
      setShowDropdown(results.length > 0);
    }, [results]);

  const handleSearch = async () => {
    if (!query.trim()) return;

    if(!handleSearch){
      setHasSearched(true)
    }
    setLoading(true);
    setError(null);

    try {
      await onSearch(query);
    } catch (err) {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='relative w-full max-w-lg mx-auto'>
      {/* Search Input */}
      <div className='relative flex items-center'>
        <input
          type='text'
          placeholder='Search...'
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className='p-4 w-full pr-10 py-3 text-lg rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-600 focus:border-blue-600'
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button
          onClick={handleSearch}
          className='absolute right-2 text-gray-500 hover:text-gray-700'>
          <Search className='w-5 h-5' />
        </button>
      </div>
      {<div ref={dropdownRef} className='absolute w-full bg-white shadow-lg rounded-lg mt-1 z-50 max-h-60 overflow-y-auto'>
        {/* Loading State */}
        {loading && (
          <div className='flex justify-center items-center mt-4'>
            <Loader2 className='animate-spin text-gray-500 w-6 h-6' />
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className='flex items-center text-red-500 mt-4'>
            <AlertCircle className='w-5 h-5 mr-2' />
            <span>{error}</span>
          </div>
        )}

        {/* No Results */}
        {hasSearched && !loading && !error && query && results.length === 0 && (
          <p className='text-gray-500 text-center mt-4'>No results found.</p>
        )}

        {/* Results List */}
        {!loading && showDropdown &&
          results.length > 0 &&
          results.map((item, index) => <div onClick={()=>{
            setShowDropdown(false);
          }}>{renderItem(item)}</div>)}
      </div>}
    </div>
  );
}
