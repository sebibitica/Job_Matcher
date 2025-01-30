import React from 'react';
import { UnifiedJob } from '../types/Job';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import deleteIcon from '../assets/delete.svg';

interface JobCardProps {
  job: UnifiedJob;
  onDelete?: (applicationId: string) => void;
}

const JobCard: React.FC<JobCardProps> = ({ job, onDelete}) => {
  const scorePercentage = (job._score * 100).toFixed(1);
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleClick = () => {
    navigate(`/job/${job._id}`, { state: { job } });
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent the card's onClick from firing
    if (!user || !job) return;

    try {
      const token = await user.getIdToken();
      await axios.delete(`http://127.0.0.1:8000/applied_jobs/${job.application_id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if(onDelete){
        onDelete(job._id);
      }
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

  return (
    <div className="job-card" onClick={handleClick} style={{ cursor: 'pointer' }}>
      {job._score === -999 ? (
        <button className="delete-btn" onClick={handleDelete} >
          <img src={deleteIcon} alt="Delete" style={{width : "20px", height: "20px"}}/>
        </button>
      ) : (
        <div className="score-badge">{scorePercentage}% Match</div>
      )}
      <h3>{job._source.job_title}</h3>
      <p className="company">{job._source.company}</p>
      <p className="location">{job._source.location.city}, {job._source.location.country}</p>
      {job.applied_date && (
        <p className="applied-date">Applied on: {formatDate(job.applied_date)}</p>
      )}
    </div>
  );
};

export default JobCard;