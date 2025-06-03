import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';

// Mock JobList and FileUpload
vi.mock('../JobList', () => ({
  __esModule: true,
  default: () => <div data-testid="job-list">JobList</div>,
}));
vi.mock('../FileUpload', () => ({
  __esModule: true,
  default: () => <div data-testid="file-upload">FileUpload</div>,
}));

// Mock axios
vi.mock('axios', () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: [] }),
    post: vi.fn().mockResolvedValue({ data: [] }),
  },
}));


const renderHomePage = (user: any, jobs: any[] = [], message = '', isLoading = false) => {
  // Mock useAuth
  vi.doMock('../../context/AuthContext', () => ({
    useAuth: () => ({ user }),
  }));

  return import('../HomePage').then(({ default: HomePage }) =>
    render(
      <MemoryRouter>
        <HomePage
          file={null}
          onFileChange={() => {}}
          onGetJobs={() => {}}
          jobs={jobs}
          message={message}
          isLoading={isLoading}
        />
      </MemoryRouter>
    )
  );
};

describe('HomePage', () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it('shows search bar and matched jobs for logged-in user', async () => {
    await renderHomePage({ displayName: 'Seb' }, [{ id: 1 }]);
    await waitFor(() => {
        expect(screen.getByPlaceholderText(/search for jobs/i)).toBeInTheDocument();
        expect(screen.getByText(/Hi Seb/i)).toBeInTheDocument();
        expect(screen.getByTestId('job-list')).toBeInTheDocument();
    });
  });

  it('shows file upload and benefits for logged-out user', async () => {
    await renderHomePage(null, []);
    await waitFor(() => {
      expect(screen.getByTestId('file-upload')).toBeInTheDocument();
      expect(screen.getByText(/why create an account/i)).toBeInTheDocument();
    });
  });

  it('shows matched jobs for logged-out user', async () => {
    await renderHomePage(null, [{ id: 1 }]);
    await waitFor(() => {
      expect(screen.getByText(/your resume matches these jobs/i)).toBeInTheDocument();
      expect(screen.getByTestId('job-list')).toBeInTheDocument();
    });
  });

  it('shows error message if message is not successful', async () => {
    await renderHomePage(null, [], 'Something went wrong');
    await waitFor(() => {
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    });
  });
});