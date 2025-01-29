// HomePage.tsx
import { useAuth } from '../context/AuthContext';
import FileUpload from './FileUpload';
import JobList from './JobList';
import { JobResult } from '../types/Job';

interface HomePageProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
  onUpload: () => void;
  jobs: JobResult[];
  message: string;
  isLoading: boolean;
}

const HomePage = ({
  file,
  onFileChange,
  onUpload,
  jobs,
  message,
  isLoading,
}: HomePageProps) => {
  const { user } = useAuth();

  return (
    <>
      <FileUpload
        onFileChange={onFileChange}
        onUpload={onUpload}
        selectedFile={file}
        isLoading={isLoading}
      />
      {user && (
        <div className="save-message">
          HEY, {user.displayName}! YOU CAN SAVE YOUR RESUME
        </div>
      )}
      {message && (
        <div
          className={`message ${
            message.includes('successful') ? 'success' : 'error'
          }`}
        >
          {message}
        </div>
      )}
      {jobs.length > 0 && <JobList jobs={jobs} />}
    </>
  );
};

export default HomePage;