import React from 'react';
import './ProgressBar.css';

interface ProgressBarProps {
  progress: number;
  status?: 'processing' | 'completed' | 'error';
  fileName?: string;
  currentStep?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ 
  progress, 
  status = 'processing', 
  fileName,
  currentStep 
}) => {
  const getStatusIcon = () => {
    switch(status) {
      case 'completed':
        return <i className="fas fa-check-circle"></i>;
      case 'error':
        return <i className="fas fa-exclamation-circle"></i>;
      default:
        return <i className="fas fa-spinner fa-spin"></i>;
    }
  };

  const getStatusColor = () => {
    switch(status) {
      case 'completed':
        return 'progress-success';
      case 'error':
        return 'progress-error';
      default:
        return 'progress-active';
    }
  };

  return (
    <div className={`progress-container ${getStatusColor()}`}>
      <div className="progress-header">
        <div className="progress-info">
          {getStatusIcon()}
          {fileName && <span className="progress-filename">{fileName}</span>}
        </div>
        <span className="progress-percentage">{Math.round(progress)}%</span>
      </div>
      
      <div className="progress-bar-wrapper">
        <div 
          className="progress-bar-fill" 
          style={{ width: `${progress}%` }}
        >
          <div className="progress-bar-glow"></div>
        </div>
      </div>
      
      {currentStep && (
        <div className="progress-step">
          <span className="progress-step-text">{currentStep}</span>
        </div>
      )}
    </div>
  );
};

export default ProgressBar;