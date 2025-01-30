import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const Header = () => {
  const { user, logout, isLoading } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="app-header">
      <div className="header-content">
        <Link to="/" className="header-logo">
            <h1>Job Matcher</h1>
        </Link>
        <div className="nav-links">
          {user && (
            <Link to="/applied" className="nav-link">
              Applied Jobs
            </Link>
          )}
          <div className="auth-status">
            {!isLoading && (
              user ? (
                <button onClick={logout} className="logout-button">
                  Logout
                </button>
              ) : (
                <button 
                  onClick={() => navigate('/login')} 
                  className="login-button"
                >
                  Login
                </button>
              )
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;