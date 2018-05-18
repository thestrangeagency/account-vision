import React from 'react';
import PropTypes from 'prop-types';

export default function File({
  date, name, onClickDelete, onClickEdit, size, frozen,
}) {
  const iconSize = 48;
  return (
    <div className="file-upload d-flex align-items-center">
      <div className="md-mx-2">
        <img src="/static/svg/icon_file.svg" width={iconSize} height={iconSize} alt="file" />
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
          <img src="/static/svg/icon_edit.svg" width={iconSize} height={iconSize} alt="edit" />
        </button>
        <button
          type="button"
          className="close px-2"
          aria-label="Remove"
          onClick={onClickDelete}
        >
          <img src="/static/svg/icon_delete.svg" width={iconSize} height={iconSize} alt="delete" />
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
