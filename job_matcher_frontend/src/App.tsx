// App.tsx
import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import HomePage from './components/HomePage';
import JobPage from './components/JobPage';
import Login from './components/Login';
import Register from './components/Register';
import { AuthProvider } from './context/AuthContext';
import { JobResult } from './types/Job';
import axios from 'axios';

const App = () => {
  const [file, setFile] = useState<File | null>(null);
  const [jobs, setJobs] = useState<JobResult[]>([]);
  const [message, setMessage] = useState('');
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
    <AuthProvider>
      <Router>
        <Header />
        <div className="app-container">
          <main className="main-content">
            <Routes>
              <Route
                path="/"
                element={
                  <HomePage
                    file={file}
                    onFileChange={setFile}
                    onUpload={handleUpload}
                    jobs={jobs}
                    message={message}
                    isLoading={isLoading}
                  />
                }
              />
              <Route path="/job/:id" element={<JobPage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;