/// <reference types="vitest/globals" />
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProfileManual from '../ProfileManual';

// Mock useAuth
vi.mock('../../context/AuthContext', () => ({
  useAuth: () => ({ user: { getIdToken: async () => 'token' } }),
}));

// Mock axios
vi.mock('axios', () => ({
  default: {
    post: vi.fn(() => Promise.resolve({ data: {} })),
  },
}));

describe('ProfileManual', () => {
  const mockOnComplete = vi.fn();
  const mockOnBack = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all section headers', () => {
    render(<ProfileManual onComplete={mockOnComplete} onBack={mockOnBack} />);
    
    expect(screen.getByText('Complete Profile Manually')).toBeInTheDocument();
    expect(screen.getByText('Experience')).toBeInTheDocument();
    expect(screen.getByText('Education')).toBeInTheDocument();
    expect(screen.getByText('Skills')).toBeInTheDocument();
  });

  it('renders add buttons for each section', () => {
    render(<ProfileManual onComplete={mockOnComplete} onBack={mockOnBack} />);
    
    expect(screen.getByText('+ Add Experience')).toBeInTheDocument();
    expect(screen.getByText('+ Add Education')).toBeInTheDocument();
    expect(screen.getByText('+ Add Skill')).toBeInTheDocument();
  });

  it('adds new field when add button is clicked', () => {
    render(<ProfileManual onComplete={mockOnComplete} onBack={mockOnBack} />);
    
    const addExperienceButton = screen.getByText('+ Add Experience');
    const initialTextareas = screen.getAllByRole('textbox');
    const initialCount = initialTextareas.length;

    fireEvent.click(addExperienceButton);
    
    const updatedTextareas = screen.getAllByRole('textbox');
    expect(updatedTextareas.length).toBe(initialCount + 1);
  });

  it('calls onBack when back button is clicked', () => {
    render(<ProfileManual onComplete={mockOnComplete} onBack={mockOnBack} />);
    
    const backButton = screen.getByText('←');
    fireEvent.click(backButton);
    
    expect(mockOnBack).toHaveBeenCalled();
  });

  it('shows submit button in initial state', () => {
    render(<ProfileManual onComplete={mockOnComplete} onBack={mockOnBack} />);
    
    const submitButton = screen.getByText('Submit');
    expect(submitButton).toBeInTheDocument();
    expect(submitButton).not.toBeDisabled();
  });
});