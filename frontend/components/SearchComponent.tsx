'use client';
import React, { useEffect, useRef, useState } from 'react';
import { Loader2, Search, AlertCircle } from 'lucide-react';

interface SearchComponentProps<T> {
  /**
   * Function to execute the search query.
   * @param query - The search query string.
   */
  onSearch: (query: string) => void;

  /**
   * Function to render each item in the search results.
   * @param item - The item to render.
   * @returns A React node representing the rendered item.
   */
  renderItem: (item: T) => React.ReactNode;

  /**
   * Array of search results.
   */
  results: T[];
}

export default function SearchComponent<T>({
  onSearch,
  renderItem,
  results = [],
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
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    setShowDropdown(results.length > 0);
    setLoading(false);
  }, [results]);

  const handleSearch = () => {
    if (!query.trim()) return;

    if (!hasSearched) {
      setHasSearched(true);
    }
    setLoading(true);
    setError(null);

    try {
      onSearch(query);
    } catch (err) {
      console.log('Error: ', err);
      setError('Something went wrong. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="relative w-full">
      {/* Search Input */}
      <div className="relative flex items-center">
        <input
          type="text"
          placeholder="Search..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="me-2 w-full rounded-lg border border-gray-300 px-2 py-1 text-lg focus:border-blue-600 focus:ring-2 focus:ring-blue-600"
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        />
        {loading ? (
          <div className="absolute right-2 text-gray-500">
            <Loader2 className="h-6 w-6 animate-spin text-gray-500" />
          </div>
        ) : (
          <button
            onClick={handleSearch}
            className="absolute right-4 text-gray-500 hover:text-gray-700"
          >
            <Search className="h-5 w-5" />
          </button>
        )}
      </div>
      {
        <div
          ref={dropdownRef}
          className="absolute z-50 mt-1 max-h-60 w-full overflow-y-auto rounded-lg bg-white shadow-lg"
        >
          {/* Error State */}
          {error && (
            <div className="mt-4 flex items-center text-red-500">
              <AlertCircle className="mr-2 h-5 w-5" />
              <span>{error}</span>
            </div>
          )}

          {/* No Results */}
          {hasSearched && !loading && !error && query && results.length === 0 && (
            <p className="mt-4 text-center text-gray-500">No results found.</p>
          )}

          {/* Results List */}
          {!loading &&
            showDropdown &&
            results.length > 0 &&
            results.map((item, index) => (
              <div
                key={index}
                onClick={() => {
                  setShowDropdown(false);
                }}
              >
                {renderItem(item)}
              </div>
            ))}
        </div>
      }
    </div>
  );
}
