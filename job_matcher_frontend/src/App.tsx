import React, { useState } from 'react';
import axios from 'axios';
import { JobResult } from './types/Job';
import FileUpload from './components/FileUpload';
import JobList from './components/JobList';
import JobPage from './components/JobPage';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import './App.css';

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [jobs, setJobs] = useState<JobResult[]>([]);
  const [message, setMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setIsLoading(true);
      const response = await axios.post(
        'http://127.0.0.1:8000/get_job_matches',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
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
    <Router>
      <div className="app-container">
        <ConditionalHeader />

        <main className="main-content">
          <Routes>
            <Route path="/" element={
              <>
                <FileUpload
                  onFileChange={setFile}
                  onUpload={handleUpload}
                  selectedFile={file}
                  isLoading={isLoading}
                />

                {message && (
                  <div className={`message ${message.includes('successful') ? 'success' : 'error'}`}>
                    {message}
                  </div>
                )}

                {jobs.length > 0 && <JobList jobs={jobs} />}
              </>
            } />
            <Route path="/job/:id" element={<JobPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

const ConditionalHeader = () => {
  const location = useLocation();
  
  if (location.pathname !== '/') {
    return (
      <header className="app-header">
        <h1>Job Match Finder</h1>
      </header>
    );
  }

  return (
    <header className="app-header">
      <h1>Job Match Finder</h1>
      <p>Upload your resume to discover your best job matches</p>
    </header>
  );
};

export default App;