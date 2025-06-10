import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import '../styles/Profile.css';
import { API_URL } from '../config/config.ts';
import ProfileUpload from './ProfileUpload';

const ProfilePage = () => {
  const { user } = useAuth();
  const [profileStatus, setProfileStatus] = useState<'loading' | 'complete' | 'incomplete'>('loading');
  const [profileStructured, setProfileStructured] = useState<any>(null);
  const [editMode, setEditMode] = useState(false);
  const [form, setForm] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [showUpdateOptions, setShowUpdateOptions] = useState(false);

  const emptyProfile = {
    summary: '',
    experience: [],
    education: [],
    skills: []
  };

  // Check profile status and load data if profile is complete
  useEffect(() => {
    const checkProfileStatus = async () => {
      if (!user) return;
      
      try {
        const token = await user.getIdToken();
        
        const statusRes = await axios.get(`${API_URL}/profile/is_complete`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        
        if (statusRes.data.status === 'complete') {
          setProfileStatus('complete');
          
          const dataRes = await axios.get(`${API_URL}/profile/data`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          
          setProfileStructured(dataRes.data);
          setForm(dataRes.data);
        } else {
          setProfileStatus('incomplete');
          setForm(emptyProfile);
          // For new profiles, start in edit mode
          setEditMode(true);
        }
      } catch (error) {
        console.error('Error checking profile status:', error);
        setProfileStatus('incomplete');
        setForm(emptyProfile);
        setEditMode(true);
      }
    };
    
    checkProfileStatus();
  }, [user]);

  // Handle form changes
  const handleChange = (section: string, idx: number, field: string, value: string) => {
    setForm((prev: any) => {
      const updated = { ...prev };
      if (Array.isArray(updated[section])) {
        updated[section] = updated[section].map((item: any, i: number) =>
          i === idx ? { ...item, [field]: value } : item
        );
      }
      return updated;
    });
  };

  const handleSkillChange = (idx: number, value: string) => {
    setForm((prev: any) => {
      const updated = { ...prev };
      updated.skills = updated.skills.map((s: string, i: number) => (i === idx ? value : s));
      return updated;
    });
  };

  const handleSummaryChange = (value: string) => {
    setForm((prev: any) => ({ ...prev, summary: value }));
  };

  // Add new experience/education/skill
  const addItem = (section: string, emptyObj: any) => {
    setForm((prev: any) => ({
      ...prev,
      [section]: [...(prev[section] || []), emptyObj],
    }));
  };

  const removeItem = (section: string, idx: number) => {
    setForm((prev: any) => ({
      ...prev,
      [section]: prev[section].filter((_: any, i: number) => i !== idx),
    }));
  };

  // Save profile
  const handleSave = async () => {
    setSaving(true);
    try {
      if (!user) return;
      const token = await user.getIdToken();
      
      await axios.post(
        `${API_URL}/profile/set_by_text`,
        { profile_text: JSON.stringify(form) },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setProfileStructured(form);
      setProfileStatus('complete');
      setEditMode(false);
    } catch (e) {
      alert('Failed to update profile.');
    }
    setSaving(false);
  };

  const handleUploadComplete = async () => {
    setShowUpload(false);
    window.location.reload();
  };

  if (profileStatus === 'loading') {
    return <div className="profile-loading">Loading profile...</div>;
  }

  if (showUpload) {
    return <ProfileUpload onComplete={handleUploadComplete} onBack={() => setShowUpload(false)} />;
  }

  return (
    <div className="profile-main-container">
      <h1>
        Hi, {user?.displayName || user?.email || 'User'}
      </h1>
      
      {profileStatus === 'incomplete' && (
        <div className="profile-welcome-message">
          <p>Complete your profile to start matching with jobs that fit your skills and experience.</p>
          <div className="profile-options">
            <button className="option-btn upload-option" onClick={() => setShowUpload(true)}>
              Upload Your CV
            </button>
            <p className="option-separator">or</p>
            <p className="manual-option-text">Complete your profile manually below</p>
          </div>
        </div>
      )}
      
      {profileStatus === 'complete' && !editMode && (
        <div className="profile-actions">
          {showUpdateOptions ? (
            <div className="update-options">
              <p>Choose how to update your profile:</p>
              <button className="option-btn upload-option" onClick={() => setShowUpload(true)}>
                Upload New CV
              </button>
              <p className="option-separator">or</p>
              <button className="edit-btn" onClick={() => {
                setEditMode(true);
                setShowUpdateOptions(false);
              }}>
                Edit Manually
              </button>
              <button className="cancel-btn" onClick={() => setShowUpdateOptions(false)}>
                Cancel
              </button>
            </div>
          ) : (
            <button onClick={() => setShowUpdateOptions(true)} className="update-btn">
              Update Profile
            </button>
          )}
        </div>
      )}
      
      <div className="profile-section">
        <div className="profile-header-row">
          <h2>Summary</h2>
        </div>
        {editMode ? (
          <textarea
            value={form.summary}
            onChange={(e) => handleSummaryChange(e.target.value)}
            rows={3}
            className="profile-summary-edit"
            placeholder="Write a brief summary of your professional background and goals..."
          />
        ) : (
          <p className="profile-summary">{profileStructured?.summary}</p>
        )}
      </div>

      <div className="profile-section">
        <div className="profile-header-row">
          <h2>Experience</h2>
          {editMode && (
            <button 
              onClick={() => addItem('experience', { title: '', company: '', startDate: '', endDate: '', description: '' })}
              className="add-btn"
            >
              + Add Experience
            </button>
          )}
        </div>
        <ul>
          {editMode && form.experience.length === 0 ? (
            <p className="empty-section-message">Add your work experience</p>
          ) : (
            (editMode ? form.experience : profileStructured?.experience)?.map((exp: any, idx: number) => (
              <li key={idx} className="profile-list-item">
                {editMode ? (
                  <div className="profile-edit-row">
                    <input value={exp.title} onChange={e => handleChange('experience', idx, 'title', e.target.value)} placeholder="Job Title" />
                    <input value={exp.company} onChange={e => handleChange('experience', idx, 'company', e.target.value)} placeholder="Company" />
                    <input value={exp.startDate} onChange={e => handleChange('experience', idx, 'startDate', e.target.value)} placeholder="Start Date (YYYY-MM)" />
                    <input value={exp.endDate} onChange={e => handleChange('experience', idx, 'endDate', e.target.value)} placeholder="End Date (YYYY-MM or Present)" />
                    <textarea 
                      value={exp.description} 
                      onChange={e => handleChange('experience', idx, 'description', e.target.value)} 
                      placeholder="Description" 
                      rows={3}
                      className="full-width"
                    />
                    <div className="actions">
                      <button onClick={() => removeItem('experience', idx)} className="remove-btn">Remove</button>
                    </div>
                  </div>
                ) : (
                  <div>
                    <div className="field-group">
                      <span className="field-label">Role:</span>
                      <span className="field-value">{exp.title}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Company:</span>
                      <span className="field-value">{exp.company}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Period:</span>
                      <span className="field-value">{exp.startDate} - {exp.endDate}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Description:</span>
                      <span className="field-value">{exp.description}</span>
                    </div>
                  </div>
                )}
              </li>
            ))
          )}
        </ul>
      </div>

      <div className="profile-section">
        <div className="profile-header-row">
          <h2>Education</h2>
          {editMode && (
            <button 
              onClick={() => addItem('education', { degree: '', field: '', institution: '', startDate: '', endDate: '' })}
              className="add-btn"
            >
              + Add Education
            </button>
          )}
        </div>
        <ul>
          {editMode && form.education.length === 0 ? (
            <p className="empty-section-message">Add your education history</p>
          ) : (
            (editMode ? form.education : profileStructured?.education)?.map((edu: any, idx: number) => (
              <li key={idx} className="profile-list-item">
                {editMode ? (
                  <div className="profile-edit-row">
                    <input value={edu.degree} onChange={e => handleChange('education', idx, 'degree', e.target.value)} placeholder="Degree (e.g. Bachelor)" />
                    <input value={edu.field} onChange={e => handleChange('education', idx, 'field', e.target.value)} placeholder="Field of Study" />
                    <input value={edu.institution} onChange={e => handleChange('education', idx, 'institution', e.target.value)} placeholder="Institution" />
                    <input value={edu.startDate} onChange={e => handleChange('education', idx, 'startDate', e.target.value)} placeholder="Start Date (YYYY-MM)" />
                    <input value={edu.endDate} onChange={e => handleChange('education', idx, 'endDate', e.target.value)} placeholder="End Date (YYYY-MM)" />
                    <div className="actions">
                      <button onClick={() => removeItem('education', idx)} className="remove-btn">Remove</button>
                    </div>
                  </div>
                ) : (
                  <div>
                    <div className="field-group">
                      <span className="field-label">Degree:</span>
                      <span className="field-value">{edu.degree} in {edu.field}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Institution:</span>
                      <span className="field-value">{edu.institution}</span>
                    </div>
                    <div className="field-group">
                      <span className="field-label">Period:</span>
                      <span className="field-value">{edu.startDate} - {edu.endDate}</span>
                    </div>
                  </div>
                )}
              </li>
            ))
          )}
        </ul>
      </div>

      <div className="profile-section">
        <div className="profile-header-row">
          <h2>Skills</h2>
          {editMode && (
            <button onClick={() => addItem('skills', '')} className="add-btn">+ Add Skill</button>
          )}
        </div>
        {editMode && (!form.skills || form.skills.length === 0) ? (
          <p className="empty-section-message">Add your professional skills</p>
        ) : (
          <ul className="profile-skills-list">
            {(editMode ? form.skills : profileStructured?.skills)?.map((skill: string, idx: number) => (
              <li key={idx} className={editMode ? "skill-item-edit" : ""}>
                {editMode ? (
                  <div className="skill-edit-container">
                    <input value={skill} onChange={e => handleSkillChange(idx, e.target.value)} placeholder="Skill" />
                    <button onClick={() => removeItem('skills', idx)} className="skill-remove-btn">×</button>
                  </div>
                ) : (
                  <span>{skill}</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>

      {editMode && (
      <div className="edit-actions">
        <button className="save-btn" onClick={handleSave} disabled={saving}>
          {saving ? 'Saving...' : profileStatus === 'incomplete' ? 'Create Profile' : 'Save Profile'}
        </button>
        {profileStatus === 'complete' && (
          <button className="cancel-btn edit-cancel" onClick={() => setEditMode(false)}>
            Cancel
          </button>
        )}
      </div>
    )}
    </div>
  );
};

export default ProfilePage;