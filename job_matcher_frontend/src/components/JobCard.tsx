import React from 'react';
import { JobResult } from '../types/Job';
import { useNavigate } from 'react-router-dom';

interface JobCardProps {
  job: JobResult;
}

const JobCard: React.FC<JobCardProps> = ({ job }) => {
  const scorePercentage = (job._score * 100).toFixed(1);
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/job/${job._id}`, { state: { job } });
  };

  return (
    <div className="job-card" onClick={handleClick} style={{ cursor: 'pointer' }}>
      <div className="score-badge">{scorePercentage}% Match</div>
      <h3>{job._source.job_title}</h3>
      <p className="company">{job._source.company}</p>
      <p className="location">{job._source.location.city}, {job._source.location.country}</p>
    </div>
  );
};

export default JobCard;