import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';

// Mock useNavigate
vi.mock('react-router-dom', () => {
  const actual = require('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

describe('Header', () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it('renders the logo', async () => {
    vi.doMock('../../context/AuthContext', () => ({
      useAuth: () => ({
        user: { email: 'test@example.com' },
        logout: vi.fn(),
        isLoading: false,
      }),
    }));
    const Header = (await import('../Header')).default;
    render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>
    );
    expect(screen.getByText(/Jobmatcher/i)).toBeInTheDocument();
  });

  it('shows navigation links when user is logged in', async () => {
    vi.doMock('../../context/AuthContext', () => ({
      useAuth: () => ({
        user: { email: 'test@example.com' },
        logout: vi.fn(),
        isLoading: false,
      }),
    }));
    const Header = (await import('../Header')).default;
    render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>
    );
    expect(screen.getByText(/Applied Jobs/i)).toBeInTheDocument();
    expect(screen.getByText(/AI Interview/i)).toBeInTheDocument();
    expect(screen.getByText(/Profile/i)).toBeInTheDocument();
    expect(screen.getByText(/Logout/i)).toBeInTheDocument();
  });

  it('shows login button when user is not logged in', async () => {
    vi.doMock('../../context/AuthContext', () => ({
      useAuth: () => ({
        user: null,
        logout: vi.fn(),
        isLoading: false,
      }),
    }));
    const Header = (await import('../Header')).default;
    render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>
    );
    expect(screen.getByText(/Login/i)).toBeInTheDocument();
  });

  it('toggles menu on button click', async () => {
    vi.doMock('../../context/AuthContext', () => ({
      useAuth: () => ({
        user: { email: 'test@example.com' },
        logout: vi.fn(),
        isLoading: false,
      }),
    }));
    const Header = (await import('../Header')).default;
    render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>
    );
    const menuButton = screen.getByLabelText(/toggle navigation menu/i);
    fireEvent.click(menuButton);
    expect(screen.getByText('✕')).toBeInTheDocument();
    fireEvent.click(menuButton);
    expect(screen.getByText('☰')).toBeInTheDocument();
  });
});