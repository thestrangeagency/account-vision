import React from 'react';
import PropTypes from 'prop-types';

import StepForm from '../shared/step-form/step-form';

export default class OnboardingForm extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      generalError: null,
      isDisabled: false,
      validationError: null,
      wasValidated: false,
    };

    this.onSubmit = this.onSubmit.bind(this);
  }

  onSubmit(formValues) {
    const { action, nextPage, userId } = this.props;

    action(formValues, userId)
      .then(() => {
        window.location = nextPage(formValues);
      })
      .catch((ex) => {
        const { generalError, validationError } = ex;

        this.setState({
          generalError,
          isDisabled: false,
          validationError,
        });
      });
  }

  render() {
    const { steps } = this.props;
    const {
      generalError, isDisabled, validationError, wasValidated,
    } = this.state;

    return (
      <StepForm
        generalError={generalError}
        isDisabled={isDisabled}
        onSubmit={this.onSubmit}
        steps={steps}
        validationError={validationError}
        wasValidated={wasValidated}
      />
    );
  }
}

OnboardingForm.propTypes = {
  action: PropTypes.func.isRequired,
  nextPage: PropTypes.func.isRequired,
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
  userId: PropTypes.string,
};

OnboardingForm.defaultProps = {
  steps: [],
  userId: null,
};
