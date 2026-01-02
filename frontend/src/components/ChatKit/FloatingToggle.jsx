import React from 'react';
import './chatkit-styles.css';

const FloatingToggle = ({ onClick }) => {
  return (
    <button
      className="chatkit-toggle-button"
      onClick={onClick}
      aria-label="Open chat"
    >
      💬
    </button>
  );
};

export default FloatingToggle;