import React from 'react';
import PropTypes from 'prop-types';

export default function File({
  date, name, onClickDelete, onClickEdit, size, frozen,
}) {
  return (
    <div className="file-upload d-flex align-items-center">
      <div className="mx-2">
        <i className="far fa-file fa-lg" />
      </div>
      <div className="md-mx-2 truncate w-25">
        {name}
      </div>
      <div className="ml-2 md-mx-2 d-none d-md-block file-upload__size text-nowrap truncate">
        {size}
      </div>
      <div className="mx-2">
        {date}
      </div>
      { !frozen &&
      <span>
        <button
          type="button"
          className="file-upload__edit-button px-2"
          aria-label="Edit"
          onClick={onClickEdit}
        >
          <i className="far fa-edit fa-lg" />
        </button>
        <button
          className="expense-manager__expense__button text-danger"
          aria-label="Remove"
          onClick={onClickDelete}
          type="button"
        >
          <i className="far fa-times-circle fa-lg" />
        </button>
      </span>
      }
    </div>
  );
}

File.propTypes = {
  date: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  onClickDelete: PropTypes.func.isRequired,
  onClickEdit: PropTypes.func.isRequired,
  size: PropTypes.string.isRequired,
  frozen: PropTypes.bool,
};

File.defaultProps = {
  frozen: false,
};
