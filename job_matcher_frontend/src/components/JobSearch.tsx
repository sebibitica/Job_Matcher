import { useState, FormEvent } from 'react';
import '../styles/JobSearch.css';
import { BaseJob } from '../types/Job';
import axios from 'axios';

const JobSearch = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<BaseJob[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e:FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;

    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post<BaseJob[]>('http://localhost:8000/job_search', {
        query: searchTerm,
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      setResults(response.data);
    } catch (err) {
      setError('Error searching jobs. Please try again.');
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="job-search-container">
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search for jobs..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      <div className="search-results">
        {results.length > 0 ? (
          results.map((job) => (
            <div key={job.id} className="job-card">
              <h3>{job.job_title}</h3>
              <p>Company: {job.company}</p>
              <p>Location: {job.location.city}, {job.location.country}</p>
            </div>
          ))
        ) : (
          !isLoading && <p>No results found</p>
        )}
      </div>
    </div>
  );
};

export default JobSearch;