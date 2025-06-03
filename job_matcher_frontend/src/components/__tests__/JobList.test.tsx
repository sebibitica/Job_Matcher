import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import JobList from '../JobList';
import { MemoryRouter } from 'react-router-dom';

// Mock JobCard 
vi.mock('../JobCard', () => ({
  __esModule: true,
  default: ({ job }: any) => <div>{job.job_title} - {job.company} - {job.location.country}</div>,
}));

describe('JobList', () => {
  it('renders a list of jobs', () => {
    const jobs = [
      {
        id: '1',
        job_title: 'Frontend Developer',
        company: 'Test Corp',
        location: { city: 'Berlin', country: 'Germany' },
        date_uploaded: new Date().toISOString(),
        score: 0.85,
      },
      {
        id: '2',
        job_title: 'Backend Developer',
        company: 'Backend Inc',
        location: { city: 'Munich', country: 'Germany' },
        date_uploaded: new Date().toISOString(),
        score: 0.92,
      },
    ];

    render(
      <MemoryRouter>
        <JobList jobs={jobs} />
      </MemoryRouter>
    );

    expect(screen.getByText(/Frontend Developer/i)).toBeInTheDocument();
    expect(screen.getByText(/Backend Developer/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Germany/i)).toHaveLength(2);
  });
});