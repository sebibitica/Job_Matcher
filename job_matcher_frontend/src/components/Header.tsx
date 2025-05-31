import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import '../styles/Header.css';

const Header = () => {
  const { user, logout, isLoading } = useAuth();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  // Toggle the mobile menu open/close
  const handleMenuToggle = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
  };

  return (
    <header className="app-header">
      <div className="header-content">
        <Link to="/" className="header-logo">
          <h1>Jobmatcher</h1>
        </Link>
        
        <button 
          className="menu-toggle" 
          onClick={handleMenuToggle}
          aria-label="Toggle navigation menu"
        >
          {isMenuOpen ? '✕' : '☰'}
        </button>

        <div className={`nav-links ${isMenuOpen ? 'open' : ''}`}>
          {user && (
            <>
              <Link to="/applied" className="nav-link" onClick={closeMenu}>
                Applied Jobs
              </Link>
              <Link to="/interviews" className="nav-link" onClick={closeMenu}>
                AI Interview
              </Link>
              <Link to="/profile" className="nav-link" onClick={closeMenu}>
                Profile
              </Link>
            </>
          )}
            {!isLoading && (
              user ? (
                <button onClick={() => { logout(); closeMenu(); }} className="logout-button">
                  Logout
                </button>
              ) : (
                <button 
                  onClick={() => { navigate('/login'); closeMenu(); }} 
                  className="login-button"
                >
                  Login
                </button>
              )
            )}
        </div>
      </div>
    </header>
  );
};

export default Header;