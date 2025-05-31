import { useAuth } from '../context/AuthContext';
import JobList from './JobList';
import { MatchedJob } from '../types/Job.ts';
import FileUpload from './FileUpload.tsx';
import '../styles/HomePage.css';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useSearchParams} from 'react-router-dom';
import { useRef } from 'react';
import filterIcon from '../assets/filter.svg';
import { API_URL } from '../config/config.ts';

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
  const [selectedCountry, setSelectedCountry] = useState('');
  const [selectedCity, setSelectedCity] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [countries, setCountries] = useState<string[]>([]);
  const [cities, setCities] = useState<string[]>([]);

  useEffect(() => {
    setSearchTerm(searchQuery);
  }, [searchQuery]);

  // Fetch available countries for location filter
  useEffect(() => {
    const fetchCountries = async () => {
      try {
        const response = await axios.get<string[]>(`${API_URL}/get_countries`);
        const filteredCountries = response.data.filter(country => country !== "Unknown");
        setCountries(filteredCountries);
      } catch (error) {
        console.error('Failed to fetch countries:', error);
      }
    };
    fetchCountries();
  }, []);

  // Fetch cities when a country is selected
  useEffect(() => {
    if (!selectedCountry) {
      setCities([]);
      setSelectedCity('');
      return;
    }
    const fetchCities = async () => {
      try {
        const response = await axios.get<string[]>(`${API_URL}/get_cities`, {
          params: { country: selectedCountry },
        });
        const filteredCities = response.data.filter(city => city !== "Unknown");
        setCities(filteredCities);
      } catch (error) {
        console.error('Failed to fetch cities:', error);
        setCities([]);
      }
    };
    fetchCities();
  }, [selectedCountry]);

  useEffect(() => {
    const searchJobs = async () => {
      if (!user) {
        console.warn('User not authenticated');
        return;
      }

      setIsSearching(true);
      try {
        const token = await user.getIdToken();

        const locationFilter = 
          selectedCountry || selectedCity
            ? {
                country: selectedCountry || undefined,
                city: selectedCity || undefined,
              }
            : undefined;

        const payload = {
          query: searchTerm,
          location: locationFilter,
        };

        const response = await axios.post<MatchedJob[]>(
          `${API_URL}/job_search`,
          payload,
          {
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            }
          }
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
  }, [searchTerm, user, selectedCountry, selectedCity]);

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
        setSelectedCountry('');
        listenerAddedRef.current = false; 
        document.removeEventListener('mousedown', handleClickOutside);
      }
    };
  
    if ((searchTerm || selectedCountry) && !listenerAddedRef.current) {
      document.addEventListener('mousedown', handleClickOutside);
      listenerAddedRef.current = true;
    }
  }, [searchTerm, selectedCountry]);

  return (
    <div className="homepage-container">
    {/* Search and filter section for logged-in users */}
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

          <button
            className="filter-toggle-btn"
            onClick={() => setShowFilters((prev) => !prev)}
            title="Toggle location filters"
          >
            <img src={filterIcon} alt="Filter" className="filter-icon" />
          </button>
          
          {showFilters && (
            <div className="filter-inline-container">
              <select
                value={selectedCountry}
                onChange={(e) => {
                  setSelectedCountry(e.target.value);
                  setSelectedCity('');
                }}
              >
                <option value="">Select Country</option>
                {countries.map((country) => (
                  <option key={country} value={country}>
                    {country}
                  </option>
                ))}
              </select>

              <select
                value={selectedCity}
                onChange={(e) => setSelectedCity(e.target.value)}
                disabled={cities.length === 0}
              >
                <option value="">Select City (optional)</option>
                {cities.map((city) => (
                  <option key={city} value={city}>
                    {city}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
        
        {(searchTerm || selectedCountry) && (
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

      {(searchTerm || selectedCountry) && <div className="search-backdrop" />}
      
      {/* File upload for logged-out users */}
      {!user && (
          <FileUpload
            selectedFile={file}
            onFileChange={onFileChange}
            onGetJobs={onGetJobs}
            isLoading={isLoading}
          />
      )}

      {!user && jobs.length < 1 &&(
        <div className="account-benefits">
          <h2>Why create an account?</h2>
          <ul>
            <li>
              <strong>AI Interview Practice:</strong> Get personalized interview simulations for specific jobs.
            </li>
            <li>
              <strong>Save Your Progress:</strong> Keep track of jobs you’ve applied to and revisit them anytime.
            </li>
            <li>
              <strong>Profile-Based Search:</strong> Instantly search and match jobs based on your saved profile.
            </li>
          </ul>
          <div className="benefits-cta">
            <span>Unlock your full job search potential — <a href="/register">create your free account now!</a></span>
          </div>
        </div>
      )}

      {message && !message.toLowerCase().includes('successful') && (
        <div className={`message-home ${message.includes('successful') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      {/* Show matched jobs for logged-in users */}
      {jobs.length > 0 && user && <> 
        <h2> Hi {user.displayName || ''}, </h2> 
        <h3>Your profile matches these jobs:</h3> 
        <JobList jobs={jobs}/> 
      </>}

      {/* Show matched jobs for logged-out users */}
      {jobs.length > 0 && !user && (
        <>
          <h3>Your resume matches these jobs:</h3>
          <JobList jobs={jobs}/>
        </>
      )}
    </div>
  );
};

export default HomePage;