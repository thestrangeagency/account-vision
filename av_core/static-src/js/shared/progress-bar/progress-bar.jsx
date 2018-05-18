import React from 'react';
import PropTypes from 'prop-types';

export default function ProgressBar({ progress }) {
  const normalizedProgress = Math.max(Math.min(progress, 1), 0);

  return (
    <div className="progress">
      <div
        className="progress-bar"
        role="progressbar"
        style={{ width: `${normalizedProgress * 100}%` }}
        aria-valuenow={normalizedProgress * 100}
        aria-valuemin="0"
        aria-valuemax="100"
      />
    </div>
  );
}

ProgressBar.propTypes = {
  progress: PropTypes.number,
};

ProgressBar.defaultProps = {
  progress: 0,
};
