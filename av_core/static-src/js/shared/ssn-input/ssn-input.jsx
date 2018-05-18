import React from 'react';
import PropTypes from 'prop-types';
import cx from 'classnames';

import { ssn } from '../../utils/regex';

export default function SsnInput({
  id, isValid, name, placeholder, required, initial,
}) {
  return (
    <input
      className={cx('form-control', {
        'is-valid': isValid === true,
        'is-invalid': isValid === false,
      })}
      id={id}
      name={name}
      pattern={ssn.source}
      placeholder={placeholder}
      required={required}
      type="tel"
      defaultValue={initial}
    />
  );
}

SsnInput.propTypes = {
  id: PropTypes.string.isRequired,
  isValid: PropTypes.bool,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  required: PropTypes.bool.isRequired,
  initial: PropTypes.string,
};

SsnInput.defaultProps = {
  isValid: null,
  placeholder: null,
  initial: null,
};
