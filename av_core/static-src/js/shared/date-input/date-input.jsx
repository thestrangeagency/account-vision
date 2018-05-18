import React from 'react';
import PropTypes from 'prop-types';
import cx from 'classnames';

import { date } from '../../utils/regex';

export default function DateInput({
  id, isValid, name, placeholder, required, initial,
}) {
  return (
    <input
      className={cx('form-control date-input', {
        'is-valid': isValid === true,
        'is-invalid': isValid === false,
      })}
      id={id}
      name={name}
      pattern={date.source}
      placeholder={placeholder}
      required={required}
      type="text"
      defaultValue={initial}
    />
  );
}

DateInput.propTypes = {
  id: PropTypes.string.isRequired,
  isValid: PropTypes.bool,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string.isRequired,
  required: PropTypes.bool.isRequired,
  initial: PropTypes.string,
};

DateInput.defaultProps = {
  isValid: null,
  initial: null,
};
