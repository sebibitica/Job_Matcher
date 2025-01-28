// src/components/JobPage.tsx
import React from 'react';
import { useLocation , useNavigate} from 'react-router-dom';
import { JobResult } from '../types/Job';

const JobPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const job = location.state?.job as JobResult;

  if (!job) {
    return <div className="job-page-container">Job not found</div>;
  }

  return (
    <div className="job-page-container">
      <button 
        onClick={() => navigate(-1)}
        className="back-button"
        >
        &larr; Back to Results
      </button>
      <div className="job-header">
        <h1>{job._source.job_title}</h1>
        <h2>{job._source.company}</h2>
        <p className="location">
          {job._source.location.city}, {job._source.location.country}
        </p>
        <a
          href={job._source.job_url}
          target="_blank"
          rel="noopener noreferrer"
          className="apply-button"
        >
          Apply Now
        </a>
      </div>

      <div className="job-content">
        <div dangerouslySetInnerHTML={{ __html: job._source.description }} />
      </div>
    </div>
  );
};

export default JobPage;