// // HomePage.tsx
// import { useAuth } from '../context/AuthContext';
// import FileUpload from './FileUpload';
// import JobList from './JobList';
// import { JobResult } from '../types/Job';
// import { SavedResume } from '../types/Resume';
// import '../styles/HomePage.css';

// // HomePage.tsx
// interface HomePageProps {
//   file: File | null;
//   onFileChange: (file: File | null) => void;
//   onGetJobs: () => void;
//   onUpload: (file: File) => void;
//   jobs: JobResult[];
//   message: string;
//   isLoading: boolean;
//   isUploading: boolean;
//   savedResumes: SavedResume[];
//   selectedResumeId: string | null;
//   onResumeSelect: (id: string | null) => void;
//   onDeleteResume: (id: string) => void;
// }

// const HomePage = ({
//   file,
//   onFileChange,
//   onGetJobs,
//   onUpload,
//   jobs,
//   message,
//   isLoading,
//   isUploading,
//   savedResumes,
//   selectedResumeId,
//   onResumeSelect,
//   onDeleteResume,
// }: HomePageProps) => {
//   const { user } = useAuth();

//   return (
//     <>
//       <FileUpload
//         onFileChange={onFileChange}
//         onGetJobs={onGetJobs}
//         onUpload={onUpload}
//         selectedFile={file}
//         isLoading={isLoading}
//         isUploading={isUploading}
//         savedResumes={savedResumes}
//         selectedResumeId={selectedResumeId}
//         onResumeSelect={onResumeSelect}
//         onDeleteResume={onDeleteResume}
//         isLoggedIn={!!user}
//       />
//       {message && (
//         <div className={`message ${message.includes('successful') ? 'success' : 'error'}`}>
//           {message}
//         </div>
//       )}
//       {jobs.length > 0 && <JobList jobs={jobs} />}
//     </>
//   );
// };

// export default HomePage;


// // App.tsx
// import { useState, useEffect } from 'react';
// import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// import './App.css';
// import Header from './components/Header';
// import HomePage from './components/HomePage';
// import JobPage from './components/JobPage';
// import Login from './components/Login';
// import Register from './components/Register';
// import AppliedJobsPage from './components/AppliedJobsPage';
// import { useAuth } from './context/AuthContext';
// import { JobResult} from './types/Job';
// import { SavedResume } from './types/Resume';
// import axios from 'axios';
// import ProtectedRoute from './components/ProtectedRoute';
// import InterviewSimulation from './components/InterviewSimulation';
// import ProfilePage from './components/ProfilePage';

// const App = () => {
//   const [file, setFile] = useState<File | null>(null);
//   const [jobs, setJobs] = useState<JobResult[]>([]);
//   const [message, setMessage] = useState('');
//   const [isLoading, setIsLoading] = useState(false);
//   const [savedResumes, setSavedResumes] = useState<SavedResume[]>([]);
//   const [selectedResumeId, setSelectedResumeId] = useState<string | null>(null);
//   const [isUploading, setIsUploading] = useState(false);
//   const { user } = useAuth();

//   useEffect(() => {
//     const fetchSavedResumes = async () => {
//       if (user) {
//         try {
//           const token = await user.getIdToken();
//           if (!token) return;

//           const response = await axios.get(
//             'http://127.0.0.1:8000/get_saved_resumes',
//             { headers: { Authorization: `Bearer ${token}` } }
//           );
//           setSavedResumes(response.data.response);
//         } catch (error) {
//           console.error('Error fetching saved resumes:', error);
//         }
//       } else {
//         setSavedResumes([]);
//       }
//     };
//     setJobs([]);
//     setMessage('');
//     setFile(null);
//     setSelectedResumeId(null);

//     fetchSavedResumes();
//   }, [user]);

//   const handleGetJobs = async () => {
//     try {
//       setIsLoading(true);
//       let response;

//       if (user) {
//         // Logged in - use selected resume
//         if (!selectedResumeId) {
//           setMessage('Please select a resume');
//           return;
//         }

//         const token = await user.getIdToken();
//         response = await axios.get(
//           `http://127.0.0.1:8000/get_job_matches_by_resume/${selectedResumeId}`,
//           { headers: { Authorization: `Bearer ${token}` } }
//         );

//         //simulate loading
//         await new Promise(resolve => setTimeout(resolve, 600));

//       } else {
//         // Logged out - use file upload
//         if (!file) {
//           setMessage('Please upload a resume');
//           return;
//         }

//         const formData = new FormData();
//         formData.append('file', file);
        
//         response = await axios.post(
//           'http://127.0.0.1:8000/get_job_matches_logged_out',
//           formData,
//           { headers: { 'Content-Type': 'multipart/form-data' } }
//         );
//       }

//       setJobs(response.data.results);
//       setMessage(response.data.message);
//     } catch (error) {
//       console.error('Error:', error);
//       setMessage('Failed to get job matches. Please try again.');
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleUpload = async (file: File) => {
//     if (!user) return;

//     try {
//       setIsUploading(true);
//       const formData = new FormData();
//       formData.append('file', file);

//       const token = await user.getIdToken();
//       const response = await axios.post(
//         'http://127.0.0.1:8000/upload_resume',
//         formData,
//         { 
//           headers: { 
//             'Content-Type': 'multipart/form-data',
//             Authorization: `Bearer ${token}`
//           } 
//         }
//       );

//       // wait for the resume to be indexed
//       await new Promise(resolve => setTimeout(resolve, 3000));

//       // Refresh saved resumes list
//       const resumesResponse = await axios.get(
//         'http://127.0.0.1:8000/get_saved_resumes',
//         { headers: { Authorization: `Bearer ${token}` } }
//       );
//       setSavedResumes(resumesResponse.data.response);

//       // Select the newly uploaded resume
//       const newResumeId = response.data.response._id;
//       setSelectedResumeId(newResumeId);
//       setMessage('Resume uploaded successfully');
//     } catch (error) {
//       console.error('Upload error:', error);
//       setMessage('Failed to upload resume');
//     } finally {
//       setIsUploading(false);
//     }
//   };

//   const handleDeleteResume = async (resumeId: string) => {
//     try {
//       const token = await user?.getIdToken();
//       await axios.delete(
//         `http://127.0.0.1:8000/delete_resume/${resumeId}`,
//         { headers: { Authorization: `Bearer ${token}` } }
//       );

//       if (savedResumes.length === 0){
//         setSelectedResumeId(null);
//         setSavedResumes([]);
//       }
//       setSavedResumes(prev => prev.filter(r => r._id !== resumeId));
//       if (selectedResumeId === resumeId) setSelectedResumeId(null);
//     } catch (error) {
//       console.error('Error deleting resume:', error);
//     }
//   };

//   return (
//     <Router>
//       <Header />
//       <div className="app-container">
//         <main className="main-content">
//           <Routes>
//             <Route
//               path="/"
//               element={
//                 <HomePage
//                   file={file}
//                   onFileChange={setFile}
//                   onGetJobs={handleGetJobs}
//                   onUpload={handleUpload}
//                   jobs={jobs}
//                   message={message}
//                   isLoading={isLoading}
//                   isUploading={isUploading}
//                   savedResumes={savedResumes}
//                   selectedResumeId={selectedResumeId}
//                   onResumeSelect={setSelectedResumeId}
//                   onDeleteResume={handleDeleteResume}
//                 />
//               }
//             />
//               <Route path="/job/:id" element={<JobPage />} />
//               <Route element={<ProtectedRoute />}>
//                 <Route path="/applied" element={<AppliedJobsPage />} />
//               </Route>
//               <Route element={<ProtectedRoute />}>
//                 <Route path="/interviews" element={<InterviewSimulation />} />
//               </Route>
//               <Route element={<ProtectedRoute />}>
//                 <Route path="/profile" element={<ProfilePage />} />
//               </Route>
//               <Route path="/login" element={<Login />} />
//               <Route path="/register" element={<Register />} />
//             </Routes>
//           </main>
//         </div>
//       </Router>
//   );
// };

// export default App;