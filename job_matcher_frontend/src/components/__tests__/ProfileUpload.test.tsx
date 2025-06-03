import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProfileUpload from '../ProfileUpload';
import { MemoryRouter } from 'react-router-dom';
import axios from 'axios';

// Mock useAuth
vi.mock('../../context/AuthContext', () => ({
  useAuth: () => ({ user: { getIdToken: async () => 'token' } }),
}));

vi.mock('axios', () => ({
  default: {
    post: vi.fn(() => Promise.resolve()),
  },
}));

describe('ProfileUpload', () => {
  it('renders upload section and button', () => {
    const mockOnComplete = vi.fn();
    const mockOnBack = vi.fn();

    render(
      <MemoryRouter>
        <ProfileUpload onComplete={mockOnComplete} onBack={mockOnBack} />
      </MemoryRouter>
    );

    expect(screen.getByText(/Upload Your Resume/i)).toBeInTheDocument();
    expect(screen.getByText(/Supported formats: PDF, DOCX/i)).toBeInTheDocument();
  });

  it('calls onBack when back button is clicked', () => {
    const mockOnComplete = vi.fn();
    const mockOnBack = vi.fn();

    render(
      <MemoryRouter>
        <ProfileUpload onComplete={mockOnComplete} onBack={mockOnBack} />
      </MemoryRouter>
    );

    const backButton = screen.getByText('←');
    fireEvent.click(backButton);

    expect(mockOnBack).toHaveBeenCalled();
  });

  it('handles file upload and calls onComplete', async () => {
    const mockOnComplete = vi.fn();
    const mockOnBack = vi.fn();

    render(
      <MemoryRouter>
        <ProfileUpload onComplete={mockOnComplete} onBack={mockOnBack} />
      </MemoryRouter>
    );

    const fileInput = screen.getByLabelText(/Upload Your Resume/i);
    const file = new File(['dummy content'], 'resume.pdf', { type: 'application/pdf' });

    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => {
      expect(mockOnComplete).toHaveBeenCalled();
    });
  });

  it('displays error message on upload failure', async () => {
    const mockOnComplete = vi.fn();
    const mockOnBack = vi.fn();

    const mockedAxios = axios as unknown as { post: ReturnType<typeof vi.fn> };
    mockedAxios.post.mockRejectedValueOnce(new Error('Upload error'));

    render(
      <MemoryRouter>
        <ProfileUpload onComplete={mockOnComplete} onBack={mockOnBack} />
      </MemoryRouter>
    );

    const fileInput = screen.getByLabelText(/Upload Your Resume/i);
    const file = new File(['dummy content'], 'resume.pdf', { type: 'application/pdf' });

    fireEvent.change(fileInput, { target: { files: [file] } });

    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(screen.getByText(/Failed to update profile/i)).toBeInTheDocument();
  });
});