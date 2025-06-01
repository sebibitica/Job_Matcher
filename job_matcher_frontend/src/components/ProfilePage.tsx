import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import ProfileUpload from './ProfileUpload.tsx';
import ProfileManual from './ProfileManual.tsx';
import '../styles/Profile.css';
import cvIcon from '../assets/cv.svg';
import manualIcon from '../assets/manual.svg';
import { API_URL } from '../config/config.ts';

const ProfilePage = () => {
  const { user } = useAuth();
  const [status, setStatus] = useState<'loading' | 'complete' | 'incomplete' | 'choice' | 'upload' | 'manual'>('loading');
  const [profile, setProfile] = useState<any>(null);
  const [isUpdating, setIsUpdating] = useState(false);


  const loadProfileStatus = async () => {
    const token = await user?.getIdToken();
    const res = await axios.get(`${API_URL}/profile/is_complete`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.data.status === 'complete') {
      setProfile(res.data);
      setStatus('complete');
    } else {
      setStatus('choice');
    }
  };

  useEffect(() => {
    if (user) loadProfileStatus();
  }, [user]);

  const handleCompleted = () => {
    loadProfileStatus();
  };

  if (status === 'loading') {
    return <p>Loading profile...</p>;
  }

  if (status === 'complete') {
    return (
      <div className="completed-profile">
        <div className="completed-card">
          <h2 className="completed-title">✅ Profile Completed</h2>
          <p className="completed-date">Completed on: {new Date(profile.date_created).toLocaleString()}</p>
          <button className="update-button" onClick={() => {setIsUpdating(true);setStatus('choice');}}>
            Update Profile
          </button>
        </div>
      </div>
    );
  }

  if (status === 'choice') {
    return (
      <div className="profile-container">
        {isUpdating && (
            <button className="back-button-profile" onClick={()=>{setIsUpdating(false);setStatus('complete')}}>←</button>
        )}
        <h2>Complete Your Profile</h2>
        <p>Select how you’d like to complete it:</p>
        <div className="profile-choice-cards">
          <div className="profile-card" onClick={() => setStatus('upload')}>
            <img src={cvIcon} alt="Upload Resume" />
            <h3>Upload Resume</h3>
          </div>
          <div className="profile-card" onClick={() => setStatus('manual')}>
            <img src={manualIcon} alt="Manual Entry" />
            <h3>Manual Entry</h3>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'upload') {
    return <ProfileUpload onComplete={handleCompleted} onBack={() => setStatus('choice')} />;
  }

  if (status === 'manual') {
    return <ProfileManual onComplete={handleCompleted} onBack={() => setStatus('choice')} />;
  }

  return null;
};

export default ProfilePage;
