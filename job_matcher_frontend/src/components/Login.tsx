import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Link } from 'react-router-dom';
import { FirebaseError } from 'firebase/app';
import '../styles/Auth.css';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [resetMessage, setResetMessage] = useState('');
  const { signIn, signInWithGoogle, isLoading, resetPassword } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setResetMessage('');
    try {
      await signIn(email, password);
      navigate('/');
    } catch (err) {
      if (err instanceof FirebaseError) {
        setError(`Login failed: ${err.code}`);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to log in.');
      }
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

  const handleResetPassword = async () => {
    setResetMessage('');
    setError('');
    if (!email) {
      setError('Please enter your email to reset your password.');
      return;
    }
    try {
      await resetPassword(email);
      setResetMessage('If an account exists for this email, a password reset email has been sent. Check your inbox.');
    } catch (err) {
      setError('Failed to send password reset email.');
    }
  };

  return (
    <div className="auth-container">
      <h2>Login</h2>
      {error && <div className="error-message">{error}</div>}
      {resetMessage && <div className="success-message">{resetMessage}</div>}
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      <button
        type="button"
        className="forgot-password"
        onClick={handleResetPassword}
        disabled={isLoading}
      >
        Forgot password?
      </button>
      <button 
        onClick={handleGoogleSignIn} 
        className="google-button"
        disabled={isLoading}
      >
        Sign in with Google
      </button>
      <div className="auth-links">
        Don't have an account? <Link to="/register">Register</Link>
      </div>
    </div>
  );
}