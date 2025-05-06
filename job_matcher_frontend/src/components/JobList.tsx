import React from 'react';
import { MatchedJob, AppliedJob } from '../types/Job';
import JobCard from './JobCard';
import '../styles/JobList.css';

interface JobListProps {
  jobs: (MatchedJob | AppliedJob)[];
  onDelete?: (jobId: string) => void;
}

const JobList: React.FC<JobListProps> = ({ jobs, onDelete}) => {
  return (
    <div className="job-list">
      {jobs.map((job) => (
        <JobCard key={job.id} job={job} onDelete={onDelete}/>
      ))}
    </div>
  );
};

export default JobList;