import React from 'react';
import PropTypes from 'prop-types';
import cx from 'classnames';

import DateInput from '../../../shared/date-input/date-input';
import SsnInput from '../../../shared/ssn-input/ssn-input';
import { formatDateInput, formatDateOutput } from '../../../utils';

export default class StepFormStep extends React.Component {
  static isValid(inputEl) {
    const { value } = inputEl;
    const isRequired = inputEl.hasAttribute('required');

    const needsValue = isRequired && value === '';
    const matches = inputEl.hasAttribute('pattern')
      ? new RegExp(inputEl.getAttribute('pattern')).test(value)
      : true;

    const isValid = !needsValue && matches;
    return isValid;
  }

  constructor(props) {
    super(props);

    this.state = {
      invalidFieldNames: [],
    };

    this.inputEls = [];

    this.onAdvance = this.onAdvance.bind(this);
    this.onKeyUp = this.onKeyUp.bind(this);
  }

  componentDidMount() {
    this.inputEls = this.el.querySelectorAll('input, select');

    this.checkFocus();
  }

  componentDidUpdate() {
    this.checkFocus();
  }

  onAdvance() {
    const invalidFieldNames = [];
    const values = {};
    this.inputEls.forEach((inputEl, index) => {
      if (!StepFormStep.isValid(inputEl)) {
        invalidFieldNames.push(inputEl.getAttribute('name'));
      } else {
        const { value } = inputEl;
        const { type } = this.props.inputs[index];
        const formattedValue = type === 'DATE' ? formatDateInput(value) : value;
        values[inputEl.name] = formattedValue;
      }
    });

    if (invalidFieldNames.length > 0) {
      this.setState({ invalidFieldNames });
      return;
    }

    this.setState({ invalidFieldNames: [] });

    this.props.onSetValues(values, () => {
      this.props.onClickNext();
    });
  }

  onClickBinary(name, value) {
    this.props.onSetValues({ [name]: value }, () => {
      this.props.onClickNext();
    });
  }

  onKeyUp(e) {
    // if user pressed enter key
    if (e.which === 13) {
      this.onAdvance();
    }

    e.preventDefault();
    e.stopPropagation();
  }

  checkFocus() {
    if (!this.props.isFocused) {
      return;
    }

    if (this.inputEls.length > 0) {
      this.inputEls[0].focus();
    }
  }

  renderFields() {
    const { inputs } = this.props;
    return inputs.map((input, index) => this.renderField(input, index));
  }

  renderField(field, key) {
    const { inputProps, type } = field;
    const {
      binaryChoices,
      label,
      name,
      required,
      pattern,
      placeholder,
      selectChoices,
      type: inputType,
      initial,
    } = inputProps;
    const { invalidFieldNames } = this.state;
    const binaryChoice1 = binaryChoices && binaryChoices[0];
    const binaryChoice2 = binaryChoices && binaryChoices[1];

    // we only display .is-invalid class, so if field is valid,
    // set isValid to null so we don't display .is-valid class.
    const isValid = invalidFieldNames.indexOf(name) === -1 ? null : false;

    let node = null;

    switch (type) {
      case 'TEXT':
        node = (
          <div className="form-group" key={key}>
            <label htmlFor={`input_${name}`}>
              {label}
              {required && <sup className="text-danger">*</sup>}
            </label>
            <input
              className={cx('form-control', {
                'is-valid': isValid === true,
                'is-invalid': isValid === false,
              })}
              id={`input_${name}`}
              name={name}
              pattern={pattern}
              placeholder={placeholder}
              required={required}
              type={inputType || 'text'}
              defaultValue={initial}
            />
            {!isValid &&
            <div className="invalid-feedback">This field is required.</div>
            }
          </div>
        );
        break;
      case 'BINARY':
        node = (
          <div className="form-group" key={key}>
            <p>{label}</p>
            <button
              className="btn btn-primary w-100 mb-3"
              onClick={binaryChoice1 && binaryChoice1.onClick
                ? binaryChoice1.onClick
                : () => this.onClickBinary(name, true)}
              type="button"
            >
              {binaryChoice1 ? binaryChoice1.text : 'Yes'}
            </button>
            <button
              className="btn btn-primary w-100 mb-3"
              onClick={binaryChoice2 && binaryChoice2.onClick
                ? binaryChoice2.onClick
                : () => this.onClickBinary(name, false)}
              type="button"
            >
              {binaryChoice2 ? binaryChoice2.text : 'No'}
            </button>
          </div>
        );
        break;
      case 'DATE':
        node = (
          <div className="form-group" key={key}>
            <label htmlFor={`input_${name}`}>
              {label}
              {required && <sup className="text-danger">*</sup>}
            </label>
            <DateInput
              id={`input_${name}`}
              isValid={isValid}
              name={name}
              placeholder={placeholder}
              required={required}
              initial={formatDateOutput(initial)}
            />
            {!isValid &&
            <div className="invalid-feedback">Please check the date format.</div>
            }
          </div>
        );
        break;
      case 'SSN':
        node = (
          <div className="form-group" key={key}>
            <label htmlFor={`input_${name}`}>
              {label}
              {required && <sup className="text-danger">*</sup>}
            </label>
            <SsnInput
              id={`input_${name}`}
              isValid={isValid}
              name={name}
              required={required}
              placeholder={placeholder}
              initial={initial}
            />
            {!isValid &&
            <div className="invalid-feedback">Please enter a valid social security number.</div>
            }
            <small className="form-text text-muted">
              Please enter a 9 digit number without dashes. We comply with federal standards to protect access to your personal information.
            </small>
          </div>
        );
        break;
      case 'SELECT':
        node = (
          <div className="form-group" key={key}>
            <label htmlFor={`input_${name}`}>
              {label}
              {required && <sup className="text-danger">*</sup>}
            </label>
            <select
              className={cx('form-control', {
                'is-valid': isValid === true,
                'is-invalid': isValid === false,
              })}
              defaultValue={initial}
              id={`input_${name}`}
              name={name}
              required={required}
            >
              {selectChoices.map(choice => (
                <option key={choice.value} value={choice.value}>
                  {choice.text}
                </option>
              ))}
            </select>
            {!isValid &&
            <div className="invalid-feedback">This field is required.</div>
            }
          </div>
        );
        break;
      default:
        node = null;
    }

    return node;
  }

  render() {
    const {
      hasBackButton,
      hasNextButton,
      id,
      isDisabled,
      isFocused,
      onClickBack,
      nextText,
      prevText,
    } = this.props;

    return (
      <div
        aria-selected={isFocused}
        className={cx('step-form-step row', {
          'step-form-step--hidden': !isFocused,
        })}
        id={id}
        onKeyUp={this.onKeyUp}
        ref={(ref) => {
          this.el = ref;
        }}
        role="option"
        tabIndex="-1"
      >
        <div className="col">
          {this.renderFields()}
          <div className="row justify-content-end">
            {hasBackButton && (
              <div className="col col-6 mr-auto">
                <button
                  className="tx-anchor-button"
                  disabled={isDisabled}
                  onClick={onClickBack}
                  type="button"
                >
                  {prevText}
                </button>
              </div>
            )}
            {hasNextButton && (
              <div className="col col-6">
                <button
                  className="btn btn-primary w-100"
                  disabled={isDisabled}
                  onClick={this.onAdvance}
                  type="button"
                >
                  {nextText}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }
}

StepFormStep.propTypes = {
  hasBackButton: PropTypes.bool,
  hasNextButton: PropTypes.bool,
  id: PropTypes.string.isRequired,
  inputs: PropTypes.arrayOf(PropTypes.shape({
    type: PropTypes.string.isRequired,
    inputProps: PropTypes.shape({
      binaryChoices: PropTypes.arrayOf(PropTypes.shape({
        onClick: PropTypes.func,
        text: PropTypes.string,
      })),
      selectChoices: PropTypes.arrayOf(PropTypes.shape({
        text: PropTypes.string,
        value: PropTypes.string,
      })),
      label: PropTypes.string,
      name: PropTypes.string,
      required: PropTypes.bool,
      pattern: PropTypes.string,
      placeholder: PropTypes.string,
      type: PropTypes.string,
      initial: PropTypes.string,
    }).isRequired,
  })),
  isDisabled: PropTypes.bool,
  isFocused: PropTypes.bool,
  onClickBack: PropTypes.func,
  onClickNext: PropTypes.func,
  onSetValues: PropTypes.func.isRequired,
  nextText: PropTypes.string,
  prevText: PropTypes.string,
};

StepFormStep.defaultProps = {
  hasBackButton: false,
  hasNextButton: false,
  inputs: [],
  isDisabled: false,
  isFocused: false,
  onClickBack: null,
  onClickNext: null,
  nextText: 'Next',
  prevText: '← Back',
};
