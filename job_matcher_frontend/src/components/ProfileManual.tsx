import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { API_URL } from '../config/config';

const ProfileManual = ({ onComplete, onBack }: { onComplete: () => void; onBack: () => void }) => {
  const { user } = useAuth();
  const [experiences, setExperiences] = useState(['']);
  const [educations, setEducations] = useState(['']);
  const [skills, setSkills] = useState(['']);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const handleArrayChange = (index: number, value: string, setter: any, array: string[]) => {
    const updated = [...array];
    updated[index] = value;
    setter(updated);
  };

  const addField = (setter: any, array: string[]) => setter([...array, '']);

  const handleSubmit = async () => {
    const token = await user?.getIdToken();
    setSubmitting(true);

    const profile_data = {
      experience: experiences.filter(e => e.trim() !== ''),
      education: educations.filter(e => e.trim() !== ''),
      skills: skills.filter(s => s.trim() !== ''),
    };

    try {
      await axios.post(
        `${API_URL}/set_user_profile_by_text`,
        { profile_data },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      onComplete();
    } catch (err) {
      setMessage('Submission failed.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="manual-profile-page">
      <button className="back-button-profile" onClick={onBack}>←</button>
      <h2>Complete Profile Manually</h2>

      <h4>Experience</h4>
      {experiences.map((exp, i) => (
        <textarea
          key={i}
          placeholder={`Experience #${i + 1}`}
          value={exp}
          onChange={(e) => handleArrayChange(i, e.target.value, setExperiences, experiences)}
        />
      ))}
      <button className="manual-profile-page-button" onClick={() => addField(setExperiences, experiences)}>+ Add Experience</button>

      <h4>Education</h4>
      {educations.map((edu, i) => (
        <textarea
          key={i}
          placeholder={`Education #${i + 1}`}
          value={edu}
          onChange={(e) => handleArrayChange(i, e.target.value, setEducations, educations)}
        />
      ))}
      <button className="manual-profile-page-button" onClick={() => addField(setEducations, educations)}>+ Add Education</button>

      <h4>Skills</h4>
      {skills.map((skill, i) => (
        <textarea
          key={i}
          placeholder={`Skill #${i + 1}`}
          value={skill}
          onChange={(e) => handleArrayChange(i, e.target.value, setSkills, skills)}
        />
      ))}
      <button className="manual-profile-page-button" onClick={() => addField(setSkills, skills)}>+ Add Skill</button>

      <br/>
      <button
        className="manual-submit-button"
        onClick={handleSubmit}
        disabled={submitting}
        >
        {submitting ? (
            <>
            <span className="button-spinner" />
            Submitting...
            </>
        ) : (
            "Submit"
        )}
        </button>
      {message && <p>{message}</p>}
    </div>
  );
};

export default ProfileManual;
