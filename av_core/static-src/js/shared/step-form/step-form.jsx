import React from 'react';
import PropTypes from 'prop-types';
import cx from 'classnames';

import StepFormStep from './step-form-step/step-form-step';

export default class StepForm extends React.Component {
  static onSubmit(e) {
    e.preventDefault();
  }

  constructor(props) {
    super(props);

    this.state = {
      activeIndex: 0,
      formValues: {},
    };

    this.onClickBack = this.onClickBack.bind(this);
    this.onClickNext = this.onClickNext.bind(this);
    this.onSetValues = this.onSetValues.bind(this);
  }

  onClickNext(targetIndex) {
    // check if we're at the last step
    if (targetIndex === this.props.steps.length - 1) {
      this.props.onSubmit(this.state.formValues);
      return;
    }

    this.goToStep(targetIndex + 1);
  }

  onClickBack(targetIndex) {
    if (targetIndex === 0) {
      return;
    }

    this.goToStep(targetIndex - 1);
  }

  onSetValues(keyValues, callback) {
    this.setState(
      {
        formValues: {
          ...this.state.formValues,
          ...keyValues,
        },
      },
      callback,
    );
  }

  goToStep(index) {
    this.setState({ activeIndex: index });
  }

  render() {
    const { activeIndex } = this.state;
    const {
      generalError, isDisabled, steps, validationError, wasValidated,
    } = this.props;

    const hasError = generalError || validationError;

    return (
      <form
        className={cx('step-form', {
          'was-validated': wasValidated,
        })}
        noValidate
        onSubmit={StepForm.onSubmit}
      >
        {hasError && (
          <div className="alert alert-danger" role="alert">
            {generalError &&
              'Whoops, something went wrong. Please try again.'
            }
            {validationError &&
              <div>
                Please fix the following errors:
                <ul>
                  {Object.keys(validationError).map(fieldName => (
                    validationError[fieldName].map(error => (
                      <li key={`${fieldName}-${error}`}>{error}</li>
                    ))
                  ))}
                </ul>
              </div>
            }
          </div>
        )}
        {steps.map((step, index) => {
          const hasBackButton = index > 0;

          // don't render next button if there's only one field
          // and its type is BINARY
          const hasNextButton = step.inputs.length !== 1
            || step.inputs[0].type !== 'BINARY';

          return (
            /* eslint-disable react/no-array-index-key */
            <StepFormStep
              hasBackButton={hasBackButton}
              hasNextButton={hasNextButton}
              id={`step-${index}`}
              inputs={step.inputs}
              isDisabled={isDisabled}
              isFocused={index === activeIndex}
              key={index}
              onClickBack={() => this.onClickBack(index)}
              onClickNext={() => this.onClickNext(index)}
              onSetValues={this.onSetValues}
            />
            /* eslint-enable react/no-array-index-key */
          );
        })}
      </form>
    );
  }
}

StepForm.propTypes = {
  generalError: PropTypes.string,
  isDisabled: PropTypes.bool,
  onSubmit: PropTypes.func.isRequired,
  steps: PropTypes.arrayOf(PropTypes.shape({
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
  })),
  validationError: PropTypes.objectOf(PropTypes.string),
  wasValidated: PropTypes.bool,
};

StepForm.defaultProps = {
  generalError: null,
  isDisabled: false,
  steps: [],
  validationError: null,
  wasValidated: false,
};
