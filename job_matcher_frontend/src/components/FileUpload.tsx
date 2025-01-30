import React from 'react';
import { SavedResume } from '../types/Resume';
import { format } from 'date-fns';
import deleteIcon from '../assets/delete.svg';
import cvIcon from '../assets/cv.svg';

// FileUpload.tsx
interface FileUploadProps {
  onFileChange: (file: File | null) => void;
  onGetJobs: () => void;
  onUpload: (file: File) => void;
  selectedFile: File | null;
  isLoading: boolean;
  isUploading: boolean;
  savedResumes: SavedResume[];
  selectedResumeId: string | null;
  onResumeSelect: (id: string | null) => void;
  onDeleteResume: (id: string) => void;
  isLoggedIn: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileChange,
  onGetJobs,
  onUpload,
  selectedFile,
  isLoading,
  isUploading,
  savedResumes,
  selectedResumeId,
  onResumeSelect,
  onDeleteResume,
  isLoggedIn,
}) => {
  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (isLoggedIn) {
      onUpload(file);
    } else {
      onFileChange(file);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'dd/MM/yyyy HH:mm');
    } catch (e) {
      return 'N/A';
    }
  };

  return (
    <div className="upload-section">
      {isLoggedIn ? (
        <div className="saved-resumes-container">
          <div className="resumes-list">
            {savedResumes.map(resume => (
              <div 
                key={resume._id}
                className={`resume-item ${selectedResumeId === resume._id ? 'selected' : ''}`}
              >
                <div 
                  className="resume-info"
                  onClick={() => {
                    onResumeSelect(resume._id);
                    onFileChange(null);
                  }}
                >
                  <img src={cvIcon} alt="Resume" style={{width : "50px", height: "50px"}}/>
                  <span className="filename">{resume._source.filename}</span>
                  <span className="date">
                    {formatDate(resume._source.upload_date)}
                  </span>
                </div>
                <button 
                  className="delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteResume(resume._id);
                  }}
                >
                  <img src={deleteIcon} alt="Delete" style={{width : "20px", height: "20px"}}/>
                </button>
              </div>
            ))}
          </div>

          <div className="resume-actions">
            <label className="upload-new-btn">
              <input
                type="file"
                onChange={handleFileInput}
                accept=".pdf,.docx"
                disabled={isUploading}
              />
              {isUploading ? (
                <span className="uploading-text">Uploading...</span>
              ) : (
                <>
                  <span className="plus-icon">+</span>
                  Upload New Resume
                </>
              )}
            </label>

            <button
              onClick={onGetJobs}
              disabled={!selectedResumeId || isLoading}
              className="get-jobs-btn"
            >
              {isLoading ? 'Loading Jobs...' : 'Get Jobs'}
            </button>
          </div>
        </div>
      ) : (
        <div className="file-input-wrapper">
          <input
            type="file"
            id="fileInput"
            onChange={handleFileInput}
            accept=".pdf,.docx"
            key={selectedFile?.name}
          />
          <label htmlFor="fileInput" className="file-label">
            {selectedFile ? (
              <div style={{display: "flex",flexDirection: "column", alignItems: "center"}}>
                <img src={cvIcon} alt="Resume" style={{width : "50px", height: "50px"}}/>
                <span className="filename">{selectedFile.name}</span>
              </div>
            )
            : (
              <>
                  <span className="plus-icon">+ </span>
                  Upload New Resume
              </>
            )}
          </label>
          <button
            onClick={onGetJobs}
            disabled={!selectedFile || isLoading}
            className="upload-button"
          >
            {isLoading ? 'Loading Jobs...' : 'Get Jobs'}
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;