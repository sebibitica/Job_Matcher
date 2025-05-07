import React from 'react';
import { MatchedJob, AppliedJob } from '../types/Job';
import JobCard from './JobCard';
import '../styles/JobList.css';

interface JobListProps {
  jobs: (MatchedJob | AppliedJob)[];
  onDelete?: (jobId: string) => void;
  isSearchResult?: boolean;
}

const JobList: React.FC<JobListProps> = ({ jobs, onDelete, isSearchResult}) => {
  return (
    <div className={`job-list ${isSearchResult ? 'search-results' : ''}`}>
      {jobs.map((job) => (
        <JobCard key={job.id} job={job} onDelete={onDelete}/>
      ))}
    </div>
  );
};

export default JobList;