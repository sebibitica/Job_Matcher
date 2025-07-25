import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { FirebaseError } from 'firebase/app';
import '../styles/Auth.css';

export default function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [nickname, setNickname] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const { signUp, isLoading, signInWithGoogle } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (!nickname.trim()) {
      setError('Nickname is required');
      return;
    }

    try {
      await signUp(email, password, nickname);
      setSuccessMessage('Registration successful! Please check your email to verify your account.');
    } catch (err) {
      const error = err as FirebaseError;
      setError('Failed to create account. ' + error.code);
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      await signInWithGoogle();
      navigate('/');
    } catch (err) {
      setError('Failed to sign in with Google.');
    }
  };

  return (
    <div className="auth-container">
      <h2>Register</h2>
      {error && <div className="error-message">{error}</div>}
      {successMessage && (
        <>
        <div className="success-message">
          {successMessage}
        </div>
        <div className="auth-links">
          Verified your account? <Link to="/login">Login</Link>
        </div>
        </>
      )}
      {!successMessage && (
      <>
      <form onSubmit={handleSubmit}>
      <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Nickname"
          value={nickname}
          onChange={(e) => setNickname(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Creating account...' : 'Register'}
        </button>
      </form>
      <button 
        onClick={handleGoogleSignIn} 
        className="google-button"
        disabled={isLoading}
      >
        Sign in with Google
      </button>
      <div className="auth-links">
        Already have an account? <Link to="/login">Login</Link>
      </div>
      </>
      )}
    </div>
  );
}