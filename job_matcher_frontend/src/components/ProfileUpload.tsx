import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import cvIcon from '../assets/cv.svg';
import '../styles/Profile.css';
import { API_URL } from '../config/config';

const ProfileUpload = ({ onComplete, onBack }: { onComplete: () => void; onBack: () => void }) => {
  const { user } = useAuth();
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileUpload = async (file: File) => {
    if (!user) return;
    
    try {
      setIsUploading(true);
      const formData = new FormData();
      formData.append('file', file);

      const token = await user.getIdToken();
      await axios.post(
        `${API_URL}/set_user_profile_by_file`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );
    } catch (error) {
      console.error('Upload error:', error);
      setMessage('Failed to update profile');
    } finally {
      onComplete();
      setIsUploading(false);
    }
  };

  return (
    <div className="profile-upload-container">
        <button className="back-button-profile" onClick={onBack}>←</button>
        <div className="upload-section-profile">
          <label className="upload-card">
            <input
              type="file"
              onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
              accept=".pdf,.docx"
              disabled={isUploading}
            />
            <div className="upload-content">
              <img src={cvIcon} alt="Upload" className="upload-icon" />
              <div className="upload-text">
                <h3>Upload Your Resume</h3>
                <p>Supported formats: PDF, DOCX</p>
              </div>
              {isUploading && (
                <>
                  <span className="button-spinner" />
                  Uploading...
                </>)
              }
            </div>
          </label>
        </div>
      {message && <div className="profile-message">{message}</div>}
    </div>
  );
};

export default ProfileUpload;