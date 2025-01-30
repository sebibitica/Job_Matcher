// AppliedJobsPage.tsx
import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import JobList from './JobList';

const AppliedJobsPage = () => {
  const { user } = useAuth();
  const [appliedJobs, setAppliedJobs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAppliedJobs = async () => {
      if (!user) return;
      
      try {
        const token = await user.getIdToken();
        const response = await axios.get('http://127.0.0.1:8000/applied_jobs', {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        const transformedJobs = response.data.applications.map((app: any) => ({
          _id: app.job_id,
          _source: app.job_data,
          _score: -999,
          application_id: app.application_id,
          applied_date: app.applied_date
        }));

        
        setAppliedJobs(transformedJobs);
      } catch (error) {
        console.error('Error fetching applied jobs:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAppliedJobs();
  }, [user]);

  const handleDelete = (jobId: string) => {
    setAppliedJobs((prevJobs) => prevJobs.filter((job) => job._id !== jobId));
  };

  return (
    <div className="applied-jobs-page">
      <h2>Hey, {user?.displayName}!</h2>
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
    </div>
  );
};

export default AppliedJobsPage;