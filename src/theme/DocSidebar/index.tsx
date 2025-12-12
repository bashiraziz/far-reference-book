/**
 * Custom DocSidebar with search filter for FAR Parts
 */

import React, { useState } from 'react';
import DocSidebar from '@theme-original/DocSidebar';
import type DocSidebarType from '@theme/DocSidebar';
import type { WrapperProps } from '@docusaurus/types';
import './styles.css';

type Props = WrapperProps<typeof DocSidebarType>;

export default function DocSidebarWrapper(props: Props): JSX.Element {
  const [searchQuery, setSearchQuery] = useState('');

  // Filter sidebar items based on search query
  const filterSidebarItems = (items: any[], query: string): any[] => {
    if (!query.trim()) return items;

    const lowerQuery = query.toLowerCase();

    return items
      .map(item => {
        // Handle category items (like "Part 1 - FAR System")
        if (item.type === 'category') {
          const matchesLabel = item.label?.toLowerCase().includes(lowerQuery);
          const filteredItems = item.items ? filterSidebarItems(item.items, query) : [];

          // Include category if label matches OR it has matching children
          if (matchesLabel || filteredItems.length > 0) {
            return {
              ...item,
              items: filteredItems.length > 0 ? filteredItems : item.items,
              collapsed: false, // Auto-expand matching categories
            };
          }
          return null;
        }

        // Handle link items
        if (item.type === 'link') {
          const matchesLabel = item.label?.toLowerCase().includes(lowerQuery);
          const matchesDocId = item.docId?.toLowerCase().includes(lowerQuery);

          if (matchesLabel || matchesDocId) {
            return item;
          }
          return null;
        }

        return item;
      })
      .filter(Boolean);
  };

  // Create filtered sidebar
  const filteredSidebar = searchQuery.trim()
    ? filterSidebarItems(props.sidebar, searchQuery)
    : props.sidebar;

  return (
    <>
      <div className="sidebar-search-container">
        <div className="sidebar-search-wrapper">
          <svg
            className="sidebar-search-icon"
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          <input
            type="text"
            className="sidebar-search-input"
            placeholder="Search FAR Parts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Search FAR Parts"
          />
          {searchQuery && (
            <button
              className="sidebar-search-clear"
              onClick={() => setSearchQuery('')}
              aria-label="Clear search"
            >
              ×
            </button>
          )}
        </div>
        {searchQuery && (
          <div className="sidebar-search-results">
            {filteredSidebar.length} result{filteredSidebar.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>
      <DocSidebar {...props} sidebar={filteredSidebar} />
    </>
  );
}
