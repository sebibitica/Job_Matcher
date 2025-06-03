import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProfilePage from '../ProfilePage';
import { MemoryRouter } from 'react-router-dom';
import axios from 'axios';

// Mock AuthContext
vi.mock('../../context/AuthContext', () => ({
  useAuth: () => ({
    user: {
      getIdToken: async () => 'mock-token',
    },
  }),
}));

// Mock ProfileUpload and ProfileManual
vi.mock('../ProfileUpload.tsx', () => ({
  default: ({ onComplete, onBack }: any) => (
    <div>
      <p>Mock Profile Upload</p>
      <button onClick={onBack}>Back</button>
      <button onClick={onComplete}>Complete</button>
    </div>
  ),
}));

vi.mock('../ProfileManual.tsx', () => ({
  default: ({ onComplete, onBack }: any) => (
    <div>
      <p>Mock Profile Manual</p>
      <button onClick={onBack}>Back</button>
      <button onClick={onComplete}>Complete</button>
    </div>
  ),
}));

// Mock axios
vi.mock('axios');
const mockedAxios = axios as unknown as {
  get: ReturnType<typeof vi.fn>;
};

describe('ProfilePage', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        mockedAxios.get = vi.fn().mockResolvedValue({
            data: { status: 'incomplete' },
        });
    });

  it('renders loading initially', () => {
    render(<ProfilePage />);
    expect(screen.getByText(/loading profile/i)).toBeInTheDocument();
  });

  it('renders complete profile if status is complete', async () => {
    mockedAxios.get = vi.fn().mockResolvedValue({
      data: {
        status: 'complete',
        date_created: new Date().toISOString(),
      },
    });

    render(
      <MemoryRouter>
        <ProfilePage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/profile completed/i)).toBeInTheDocument();
    });
  });

  it('renders choice screen if status is incomplete', async () => {
    mockedAxios.get = vi.fn().mockResolvedValue({
      data: { status: 'incomplete' },
    });

    render(
      <MemoryRouter>
        <ProfilePage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/complete your profile/i)).toBeInTheDocument();
    });
  });

  it('can switch to upload and back to choice', async () => {
    mockedAxios.get = vi.fn().mockResolvedValue({
      data: { status: 'incomplete' },
    });

    render(
      <MemoryRouter>
        <ProfilePage />
      </MemoryRouter>
    );

    await waitFor(() => screen.getByText(/upload resume/i));

    fireEvent.click(screen.getByText(/upload resume/i));
    expect(screen.getByText(/mock profile upload/i)).toBeInTheDocument();

    fireEvent.click(screen.getByText(/back/i));
    expect(screen.getByText(/complete your profile/i)).toBeInTheDocument();
  });

  it('can switch to manual and back to choice', async () => {
    mockedAxios.get = vi.fn().mockResolvedValue({
      data: { status: 'incomplete' },
    });

    render(
      <MemoryRouter>
        <ProfilePage />
      </MemoryRouter>
    );

    await waitFor(() => screen.getByText(/manual entry/i));

    fireEvent.click(screen.getByText(/manual entry/i));
    expect(screen.getByText(/mock profile manual/i)).toBeInTheDocument();

    fireEvent.click(screen.getByText(/back/i));
    expect(screen.getByText(/complete your profile/i)).toBeInTheDocument();
  });
});
