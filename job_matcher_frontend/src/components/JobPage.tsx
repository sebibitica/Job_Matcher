// JobPage.tsx
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { UnifiedJob } from '../types/Job';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import '../styles/JobPage.css';

const JobPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const job = location.state?.job as UnifiedJob;
  const [isApplied, setIsApplied] = useState(false);
  const [isStartingInterview, setIsStartingInterview] = useState(false);

  useEffect(() => {
    const checkAppliedStatus = async () => {
      if (!user || !job) return;

      try {
        const token = await user.getIdToken();
        const response = await axios.get(`http://127.0.0.1:8000/is_applied_job/${job._id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        console.log('Is applied:', response.data);
        
        setIsApplied(response.data.is_applied);
      } catch (error) {
        console.error('Error checking applied status:', error);
      }
    };

    checkAppliedStatus();
  }, [user, job]);

  const handleApplyClick = async () => {
    if (!user) return;

    try {
      const token = await user.getIdToken();
      if (!isApplied) {
        await axios.post(
          `http://127.0.0.1:8000/apply_to_job/${job._id}`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setIsApplied(true);
      }
    } catch (error) {
      console.error('Error applying to job:', error);
    }
  };

  const handleStartInterview = async () => {
    if (!user || !job) return;

    try {
      setIsStartingInterview(true);
      const token = await user.getIdToken();
      const response = await axios.post(
        `http://127.0.0.1:8000/interviews/initiate/${job._id}`,
        {
          job_title: job._source.job_title,
          job_description: job._source.description
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Navigate to interview page with the new interview ID
      navigate('/interviews', { 
        state: { 
          newInterviewId: response.data.interview_id,
          initialMessage: response.data.ai_response 
        } 
      });
    } catch (error) {
      console.error('Error starting interview:', error);
    } finally {
      setIsStartingInterview(false);
    }
  };

  if (!job) {
    return <div className="job-page-container">Job not found</div>;
  }

  return (
    <div className="job-page-container">
      <button onClick={() => navigate(-1)} className="back-button">
        &larr; Back to Results
      </button>
      <div className="job-header">
        <h1>{job._source.job_title}</h1>
        <h2>{job._source.company}</h2>
        <p className="location">
          {job._source.location.city}, {job._source.location.country}
        </p>
        <div className="job-buttons">
          {user && (
            <>
            <button
              className={`apply-button ${isApplied ? 'applied' : ''}`}
              onClick={handleApplyClick}
            >
              {isApplied ? '✓ Applied' : 'Mark as Applied'}
            </button>
            <button 
              onClick={handleStartInterview}
              className="interview-button"
              disabled={isStartingInterview} // Disable during loading
            >
              {isStartingInterview ? 'Creating Interview...' : 'Practice Interview'}
            </button>
            </>
          )}
          <a
            href={job._source.job_url}
            target="_blank"
            rel="noopener noreferrer"
            className="external-apply-button"
          >
            External URL
          </a>
        </div>
      </div>
      <div className="job-content">
        <div dangerouslySetInnerHTML={{ __html: job._source.description }} />
      </div>
    </div>
  );
};

export default JobPage;