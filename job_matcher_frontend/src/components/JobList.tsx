import React from 'react';
import { JobResult } from '../types/Job';
import JobCard from './JobCard';

interface JobListProps {
  jobs: JobResult[];
}

const JobList: React.FC<JobListProps> = ({ jobs }) => {
  return (
    <div className="job-list">
      {jobs.map((job) => (
        <JobCard key={job._id} job={job} />
      ))}
    </div>
  );
};

export default JobList;