import React from 'react';

interface FileUploadProps {
  onFileChange: (file: File) => void;
  onUpload: () => void;
  selectedFile: File | null;
  isLoading: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileChange,
  onUpload,
  selectedFile,
  isLoading,
}) => {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      onFileChange(e.target.files[0]);
    }
  };

  return (
    <div className="upload-section">
      <div className="file-input-wrapper">
        <input
          type="file"
          id="fileInput"
          onChange={handleFileChange}
          accept=".pdf,.docx"
          key={selectedFile?.name}
        />
        <label htmlFor="fileInput" className="file-label">
          {selectedFile ? selectedFile.name : 'Choose Resume...'}
        </label>
        <button
          onClick={onUpload}
          disabled={!selectedFile || isLoading}
          className="upload-button"
        >
          {isLoading ? (
            <span className="button-loading">
              <span className="spinner"></span>
              Loading jobs...
            </span>
          ) : (
            'Get Jobs'
          )}
        </button>
      </div>
    </div>
  );
};

export default FileUpload;