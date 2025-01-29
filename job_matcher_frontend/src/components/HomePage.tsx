import { useState } from 'react';
import axios from 'axios';
import { JobResult } from '../types/Job';
import FileUpload from '../components/FileUpload';
import JobList from '../components/JobList';
import { useAuth } from '../context/AuthContext';

const HomePage = () => {
  const [file, setFile] = useState<File | null>(null);
  const [jobs, setJobs] = useState<JobResult[]>([]);
  const [message, setMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useAuth();

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);

    try {
      setIsLoading(true);
      const response = await axios.post(
        'http://127.0.0.1:8000/get_job_matches',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      setJobs(response.data.results);
      setMessage(response.data.message);
    } catch (error) {
      console.error('Error uploading file:', error);
      setMessage('Failed to get job matches. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <FileUpload
        onFileChange={setFile}
        onUpload={handleUpload}
        selectedFile={file}
        isLoading={isLoading}
      />
      {user && <div className="save-message">HEY, {user.displayName}!   YOU CAN SAVE YOUR RESUME</div>}
      {message && (
        <div className={`message ${message.includes('successful') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}
      {jobs.length > 0 && <JobList jobs={jobs} />}
    </>
  );
};

export default HomePage;