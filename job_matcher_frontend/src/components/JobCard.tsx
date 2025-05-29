import React from 'react';
import { MatchedJob, AppliedJob } from '../types/Job';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import deleteIcon from '../assets/delete.svg';
import '../styles/JobCard.css';
import { API_URL } from '../config/config';

interface JobCardProps {
  job: MatchedJob | AppliedJob;
  onDelete?: (jobId: string) => void;
}

const JobCard: React.FC<JobCardProps> = ({ job, onDelete}) => {
  const isApplied = 'application_id' in job;
  const isMatched = 'score' in job;
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleClick = () => {
    navigate(`/job/${job.id}`);
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent the card's onClick from firing
    if (!user || !isApplied) return;

    try {
      const token = await user.getIdToken();
      await axios.delete(`${API_URL}/applied_jobs/${job.application_id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      onDelete?.(job.id);
    } catch (error) {
      console.error('Error deleting application:', error);
    }
  };

  const formatDate = (dateString: string) => {
      try {
        return format(new Date(dateString), 'dd/MM/yyyy HH:mm');
      } catch (e) {
        return 'Date not available';
      }
    };

  const isNew = (() => {
    if ('date_uploaded' in job && job.date_uploaded) {
      const uploaded = new Date(job.date_uploaded);
      const now = new Date();
      return (now.getTime() - uploaded.getTime()) < 24 * 60 * 60 * 1000;
    }
    return false;
  })();

  return (
    <div className="job-card" onClick={handleClick} style={{ cursor: 'pointer' }}>
      {isNew && (
        <div className="new-badge">NEW</div>
      )}
      {isApplied? (
        <button className="delete-btn" onClick={handleDelete} >
          <img src={deleteIcon} alt="Delete" style={{width : "20px", height: "20px"}}/>
        </button>
      ) : isMatched ? (
        <div className="score-badge">{((job as MatchedJob).score * 100).toFixed(1)}% Match</div>
      ) : null}
      <h3>{job.job_title}</h3>
      <p className="company">{job.company}</p>
      {job.location.country !== "Unknown" && (
        <p className="location">
          {job.location.city !== "Unknown" 
            ? `${job.location.city}, ${job.location.country}`
            : job.location.country
          }
        </p>
      )}
      {'applied_date' in job && (
        <p className="applied-date">Applied on: {formatDate(job.applied_date)}</p>
      )}
    </div>
  );
};

export default JobCard;