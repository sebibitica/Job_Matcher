import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { FullJobDetails } from '../types/Job';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import '../styles/JobPage.css';
import { API_URL } from '../config/config';

const JobPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [job, setJob] = useState<FullJobDetails | null>(null);
  const {id} = useParams<{id: string}>();
  const [isApplied, setIsApplied] = useState(false);
  const [isStartingInterview, setIsStartingInterview] = useState(false);

  useEffect(() => {
    const checkAppliedStatus = async () => {
      if (!user || !id) return;

      try {
        const token = await user.getIdToken();
        const response = await axios.get(`${API_URL}/applied_jobs/is_applied/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        console.log('Is applied:', response.data);
        
        setIsApplied(response.data.is_applied);
      } catch (error) {
        console.error('Error checking applied status:', error);
      }
    };

    checkAppliedStatus();
  }, [user]);

  useEffect(() => {
    const fetchJobData = async () => {
      if (!id) return;

      try {
        const token = user ? await user.getIdToken() : null;
        const response = await axios.get(`${API_URL}/search_jobs/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setJob(response.data.job);
      } catch (error) {
        console.error('Error fetching job data:', error);
      }
    };

    fetchJobData();
  }, [id]);

  const handleApplyClick = async () => {
    if (!user || !job) return;

    try {
      const token = await user.getIdToken();
      if (!isApplied) {
        await axios.post(
          `${API_URL}/applied_jobs/apply/${job.id}`,
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
        `${API_URL}/interviews/initiate/${job.id}`,
        {
          job_title: job.job_title,
          job_description: job.description
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
        &larr; Back
      </button>
      <div className="job-header">
        <h1>{job.job_title}</h1>
        <h2>{job.company}</h2>
        {job.location.country !== "Unknown" && (
          <p className="location">
            {job.location.city !== "Unknown" 
              ? `${job.location.city}, ${job.location.country}`
              : job.location.country
            }
          </p>
        )}
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
              disabled={isStartingInterview}
            >
              {isStartingInterview ? 'Creating Interview...' : 'Practice Interview'}
            </button>
            </>
          )}
          <a
            href={job.job_url}
            target="_blank"
            rel="noopener noreferrer"
            className="external-apply-button"
          >
            External URL
          </a>
        </div>
      </div>
      <div className="job-content">
        <div dangerouslySetInnerHTML={{ __html: job.description }} />
      </div>
    </div>
  );
};

export default JobPage;