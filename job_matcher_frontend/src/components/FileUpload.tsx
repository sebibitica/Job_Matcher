import React from 'react';
import cvIcon from '../assets/cv.svg';
import '../styles/FileUpload.css';

// FileUpload.tsx
interface FileUploadProps {
  onFileChange: (file: File | null) => void;
  onGetJobs: () => void;
  selectedFile: File | null;
  isLoading: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileChange,
  onGetJobs,
  selectedFile,
  isLoading,
}) => {
  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    onFileChange(file);

  };

  return (
    <div className="upload-section">
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
        <div className="upload-instructions">
          <br/>
          <p>Upload your resume in PDF or DOCX format.</p>
          <h4>We will match you with the best job opportunities!</h4>
        </div>
    </div>
  );
};

export default FileUpload;