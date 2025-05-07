import { useAuth } from '../context/AuthContext';
import JobList from './JobList';
import { MatchedJob } from '../types/Job.ts';
import FileUpload from './FileUpload.tsx';
import '../styles/HomePage.css';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useSearchParams} from 'react-router-dom';
import { useRef } from 'react';

interface HomePageProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
  onGetJobs: () => void;
  jobs: MatchedJob[];
  message: string;
  isLoading: boolean;
}

const HomePage = ({
  file,
  onFileChange,
  onGetJobs,
  jobs,
  message,
  isLoading,
}: HomePageProps) => {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const searchQuery = searchParams.get('search') || '';
  const [searchTerm, setSearchTerm] = useState(searchQuery);
  const [searchResults, setSearchResults] = useState<MatchedJob[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const searchContainerRef = useRef<HTMLDivElement>(null);
  const listenerAddedRef = useRef(false);

  useEffect(() => {
    setSearchTerm(searchQuery);
  }, [searchQuery]);

  useEffect(() => {
    const searchJobs = async () => {
      if (!searchTerm.trim()) {
        setSearchResults([]);
        setIsSearching(false);
        return;
      }

      setIsSearching(true);
      try {
        const response = await axios.post<MatchedJob[]>(
          'http://localhost:8000/job_search',
          { query: searchTerm },
          { headers: { 'Content-Type': 'application/json' } }
        );
        setSearchResults(response.data);
      } catch (error) {
        console.error('Search failed:', error);
      } finally {
        setIsSearching(false);
      }
    };

    const debounceTimer = setTimeout(searchJobs, 500);
    return () => clearTimeout(debounceTimer);
  }, [searchTerm]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        searchContainerRef.current &&
        !searchContainerRef.current.contains(event.target as Node)
      ) {
        // Clicked outside the search area
        setSearchTerm('');
        setSearchResults([]);
        setSearchParams({});
        listenerAddedRef.current = false; // Reset so we can add again later
        document.removeEventListener('mousedown', handleClickOutside);
        // Clean up the event listener
      }
    };
  
    if (searchTerm && !listenerAddedRef.current) {
      // Add event listener only if search term is present
      document.addEventListener('mousedown', handleClickOutside);
      listenerAddedRef.current = true;
    }
  
    if (!searchTerm && listenerAddedRef.current) {
      // If search term is cleared, remove the event listener
      document.removeEventListener('mousedown', handleClickOutside);
      listenerAddedRef.current = false;
    }
  }, [searchTerm]);

  return (
    <div className="homepage-container">
    {user && (
      <div className="search-section" ref={searchContainerRef}>
        <div className="search-bar-container">
          <input
            type="text"
            placeholder="Search for jobs..."
            value={searchTerm}
            onChange={(e) => {
              const term = e.target.value;
              setSearchTerm(term);
              setSearchParams(term ? { search: term } : {});
            }}
            className="search-input"
          />
        </div>
        
        {(searchTerm || isSearching) && (
          <div className="search-results-container">
            {isSearching ? (
              <div className="search-status">Searching jobs...</div>
            ) : searchResults.length > 0 ? (
              <JobList jobs={searchResults} isSearchResult={true} />
            ) : (
              <div className="search-status">No jobs match your search</div>
            )}
          </div>
        )}
      </div>
    )}

      {(searchTerm || isSearching) && <div className="search-backdrop" />}

      {!user && (
        <FileUpload
          selectedFile={file}
          onFileChange={onFileChange}
          onGetJobs={onGetJobs}
          isLoading={isLoading}
        />
      )}

      {message && !message.toLowerCase().includes('successful') && (
        <div className={`message ${message.includes('successful') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      {jobs.length > 0 && user && <> <h2> Hi {user.displayName || ''}, </h2> <h3>Your profile matches these jobs:</h3> <JobList jobs={jobs}/> </> }
    </div>
  );
};

export default HomePage;