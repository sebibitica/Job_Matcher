import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import HomePage from './components/HomePage';
import JobPage from './components/JobPage';
import Login from './components/Login';
import Register from './components/Register';
import AppliedJobsPage from './components/AppliedJobsPage';
import { useAuth } from './context/AuthContext';
import {MatchedJob} from './types/Job';
import axios from 'axios';
import ProtectedRoute from './components/ProtectedRoute';
import InterviewSimulation from './components/InterviewSimulation';
import ProfilePage from './components/ProfilePage';
import { API_URL } from './config/config';

const App = () => {
  const [jobs, setJobs] = useState<MatchedJob[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { user , isLoading: authLoading} = useAuth();

  // Fetch jobs when user is authenticated
  useEffect(() => {
    if(!authLoading){
      handleGetJobs();
    }
    if (!user){
      setJobs([]);
      setMessage('');
    }
  }, [user]);

  if (authLoading) {
    return null;
  }

  // Fetch job matches for logged-in users
  const handleGetJobs = async () => {
    if (user){
      try {
        setIsLoading(true);
    
        const token = await user.getIdToken();
    
        // Check if user has completed their profile
        const profileStatusRes = await axios.get(
          `${API_URL}/is_user_profile`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
    
        if (profileStatusRes.data.status !== 'complete') {
          setMessage('Please complete your profile to get job matches.');
          return;
        }
    
        // Fetch job matches using completed profile
        const jobsRes = await axios.get(
          `${API_URL}/get_job_matches_by_profile`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
    
        setJobs(jobsRes.data.jobs);
        setMessage(jobsRes.data.message || 'Job matches retrieved.');
      } catch (error) {
        console.error('Error fetching jobs:', error);
        setMessage('Failed to get job matches. Please try again.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  // Fetch job matches for logged-out users using uploaded file
  const handleGetJobsLoggedOut = async () => {
    try {
      setIsLoading(true);
      
      if (!file) {
        return;
      }

      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(
        `${API_URL}/get_job_matches_logged_out`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      setJobs(response.data.jobs);
      setMessage(response.data.message || 'Job matches retrieved.');
    } catch (error) {
      console.error('Error:', error);
      setMessage('Failed to get job matches. Please try again.');
    }
    finally {
      setIsLoading(false);
    }
  }

  return (
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
                  jobs={jobs}
                  onGetJobs={handleGetJobsLoggedOut}
                  message={message}
                  isLoading={isLoading}
                />
              }
            />
              <Route path="/job/:id" element={<JobPage />} />
              <Route element={<ProtectedRoute />}>
                <Route path="/applied" element={<AppliedJobsPage />} />
              </Route>
              <Route element={<ProtectedRoute />}>
                <Route path="/interviews" element={<InterviewSimulation />} />
              </Route>
              <Route element={<ProtectedRoute />}>
                <Route path="/profile" element={<ProfilePage />} />
              </Route>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Routes>
          </main>
        </div>
      </Router>
  );
};

export default App;