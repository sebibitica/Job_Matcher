import { describe, it, expect,vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import JobCard from '../JobCard';
import { MemoryRouter } from 'react-router-dom';

// Mock useAuth and useNavigate
vi.mock('../../context/AuthContext', () => ({
  useAuth: () => ({ user: { getIdToken: async () => 'token' } }),
}));
vi.mock('react-router-dom', () => {
  const actual = require('react-router-dom');
  return {
    ...actual,
    useNavigate: () => () => {},
  };
});

describe('JobCard', () => {
  it('renders job title and company', () => {
    const dummyJob = {
      id: '1',
      job_title: 'Frontend Developer',
      company: 'Test Corp',
      location: { city: 'Berlin', country: 'Germany' },
      date_uploaded: new Date().toISOString(),
      score: 0.85,
    };

    render(
      <MemoryRouter>
        <JobCard job={dummyJob} />
      </MemoryRouter>
    );

    expect(screen.getByText(/Frontend Developer/i)).toBeInTheDocument();
    expect(screen.getByText(/Test Corp/i)).toBeInTheDocument();
    expect(screen.getByText(/Germany/i)).toBeInTheDocument();
  });
});