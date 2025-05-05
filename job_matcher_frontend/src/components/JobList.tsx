import React from 'react';
import { UnifiedJob } from '../types/Job';
import JobCard from './JobCard';
import '../styles/JobList.css';

interface JobListProps {
  jobs: UnifiedJob[];
  onDelete?: (applicationId: string) => void;
}

const JobList: React.FC<JobListProps> = ({ jobs, onDelete}) => {
  return (
    <div className="job-list">
      {jobs.map((job) => (
        <JobCard key={job._id} job={job} onDelete={onDelete}/>
      ))}
    </div>
  );
};

export default JobList;