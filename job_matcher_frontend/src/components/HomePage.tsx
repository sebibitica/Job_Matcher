// HomePage.tsx
import { useAuth } from '../context/AuthContext';
import JobList from './JobList';
import {MatchedJob} from '../types/Job.ts'
import FileUpload from './FileUpload.tsx';
import '../styles/HomePage.css';

interface HomePageProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
  onGetJobs: () => void;
  jobs: MatchedJob[];
  message: string;
  isLoading: boolean;
}

const HomePage = ({
  file,
  onFileChange,
  onGetJobs,
  jobs,
  message,
  isLoading,
}: HomePageProps) => {
  const { user } = useAuth();

  return (
    <div className="homepage-container">
      {!user && (
        <FileUpload
          selectedFile={file}
          onFileChange={onFileChange}
          onGetJobs={onGetJobs}
          isLoading={isLoading}
        />
      )}
      {user && <h2>Welcome, {user.displayName || 'user'}!</h2>}

      {message && (
        <div className={`message ${message.includes('successful') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      {jobs.length > 0 && <JobList jobs={jobs} />}
    </div>
  );
};

export default HomePage;
