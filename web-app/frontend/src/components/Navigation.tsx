import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import '../styles/Navigation.css';

const Navigation: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-left">
          <h1 className="nav-logo">Markitdown</h1>
          <div className="nav-links">
            <Link
              to="/"
              className={`nav-link ${isActive('/') ? 'active' : ''}`}
            >
              Dashboard
            </Link>
            <Link
              to="/storage"
              className={`nav-link ${isActive('/storage') ? 'active' : ''}`}
            >
              Storage
            </Link>
            <Link
              to="/settings"
              className={`nav-link ${isActive('/settings') ? 'active' : ''}`}
            >
              Settings
            </Link>
          </div>
        </div>
        <div className="nav-right">
          <button className="nav-icon-btn">
            <i className="fas fa-bell"></i>
            <span className="notification-dot"></span>
          </button>
          <div className="user-avatar">U</div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;