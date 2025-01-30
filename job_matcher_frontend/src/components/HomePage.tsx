// HomePage.tsx
import { useAuth } from '../context/AuthContext';
import FileUpload from './FileUpload';
import JobList from './JobList';
import { JobResult } from '../types/Job';
import { SavedResume } from '../types/Resume';

// HomePage.tsx
interface HomePageProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
  onGetJobs: () => void;
  onUpload: (file: File) => void;
  jobs: JobResult[];
  message: string;
  isLoading: boolean;
  isUploading: boolean;
  savedResumes: SavedResume[];
  selectedResumeId: string | null;
  onResumeSelect: (id: string | null) => void;
  onDeleteResume: (id: string) => void;
}

const HomePage = ({
  file,
  onFileChange,
  onGetJobs,
  onUpload,
  jobs,
  message,
  isLoading,
  isUploading,
  savedResumes,
  selectedResumeId,
  onResumeSelect,
  onDeleteResume,
}: HomePageProps) => {
  const { user } = useAuth();

  return (
    <>
      <FileUpload
        onFileChange={onFileChange}
        onGetJobs={onGetJobs}
        onUpload={onUpload}
        selectedFile={file}
        isLoading={isLoading}
        isUploading={isUploading}
        savedResumes={savedResumes}
        selectedResumeId={selectedResumeId}
        onResumeSelect={onResumeSelect}
        onDeleteResume={onDeleteResume}
        isLoggedIn={!!user}
      />
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