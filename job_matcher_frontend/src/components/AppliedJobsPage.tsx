import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { AppliedJob } from '../types/Job';
import axios from 'axios';
import JobList from './JobList';
import { API_URL } from '../config/config';

const AppliedJobsPage = () => {
  const { user } = useAuth();
  const [appliedJobs, setAppliedJobs] = useState<AppliedJob[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAppliedJobs = async () => {
      if (!user) return;
      
      try {
        const token = await user.getIdToken();
        const response = await axios.get(`${API_URL}/applied_jobs`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        setAppliedJobs(response.data.applications);
      } catch (error) {
        console.error('Error fetching applied jobs:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAppliedJobs();
  }, [user]);

  // Remove a job from the list after deletion
  const handleDelete = (jobId: string) => {
    setAppliedJobs((prevJobs) => prevJobs.filter((job) => job.id !== jobId));
  };

  return (
    <>
      <br/>
      <h2>Here are your applied jobs:</h2>
      {isLoading ? (
        <div>Loading applied jobs...</div>
      ) : (
        appliedJobs.length > 0 ? (
          <JobList jobs={appliedJobs} onDelete={handleDelete}/>
        ) : (
          <div>No applied jobs found</div>
        )
      )}
    </>
  );
};

export default AppliedJobsPage;