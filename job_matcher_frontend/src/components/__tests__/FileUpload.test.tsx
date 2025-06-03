import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import FileUpload from '../FileUpload';

describe('FileUpload', () => {
  it('renders upload instructions and button', () => {
    render(
      <FileUpload
        onFileChange={vi.fn()}
        onGetJobs={vi.fn()}
        selectedFile={null}
        isLoading={false}
      />
    );
    expect(screen.getByText(/Upload your resume/i)).toBeInTheDocument();
    expect(screen.getByText(/Get Jobs/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/upload new resume/i)).toBeInTheDocument();
  });

  it('shows selected file name and disables button when loading', () => {
    render(
      <FileUpload
        onFileChange={vi.fn()}
        onGetJobs={vi.fn()}
        selectedFile={new File(['resume'], 'resume.pdf', { type: 'application/pdf' })}
        isLoading={true}
      />
    );
    expect(screen.getByText(/resume.pdf/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /loading jobs/i })).toBeDisabled();
  });

  it('calls onFileChange when a file is selected', () => {
    const onFileChange = vi.fn();
    render(
      <FileUpload
        onFileChange={onFileChange}
        onGetJobs={vi.fn()}
        selectedFile={null}
        isLoading={false}
      />
    );
    const fileInput = screen.getByLabelText(/upload new resume/i) as HTMLInputElement;
    const file = new File(['resume'], 'resume.pdf', { type: 'application/pdf' });
    fireEvent.change(fileInput, { target: { files: [file] } });
    expect(onFileChange).toHaveBeenCalledWith(file);
  });

  it('calls onGetJobs when button is clicked', () => {
    const onGetJobs = vi.fn();
    render(
      <FileUpload
        onFileChange={vi.fn()}
        onGetJobs={onGetJobs}
        selectedFile={new File(['resume'], 'resume.pdf', { type: 'application/pdf' })}
        isLoading={false}
      />
    );
    const button = screen.getByRole('button', { name: /get jobs/i });
    fireEvent.click(button);
    expect(onGetJobs).toHaveBeenCalled();
  });
});