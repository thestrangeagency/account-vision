import React from 'react';
import PropTypes from 'prop-types';

import OnboardingForm from '../onboarding-form';
import OnboardingApiService from '../../services/onboarding-api-service';

export default class StatusOnboarding extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      filing_status: null,
      action: props.returnId ?
        formValues => OnboardingApiService.updateReturn(formValues, props.returnId) :
        OnboardingApiService.createReturn,
      hasFetched: false,
    };
  }

  componentDidMount() {
    this.getReturnInfo();
  }

  getReturnInfo() {
    const { returnId } = this.props;

    if (returnId) {
      OnboardingApiService.getReturnInfo(returnId)
        .then(({ filing_status }) => (
          this.setState({
            filing_status,
            hasFetched: true,
          })
        ));
    } else {
      this.setState({ hasFetched: true });
    }
  }

  render() {
    const {
      nextPage,
      nextPageAlt,
    } = this.props;

    const {
      filing_status,
      hasFetched,
      action,
    } = this.state;

    if (hasFetched) {
      return (
        <OnboardingForm
          action={action}
          nextPage={formValues =>
            (formValues.filing_status === 'MARRIED_JOINT' ? nextPage : nextPageAlt)
          }
          steps={[
            {
              inputs: [
                {
                  type: 'SELECT',
                  inputProps: {
                    label: 'Filing Status',
                    name: 'filing_status',
                    required: true,
                    selectChoices: [
                      {
                        text: '---------',
                        value: '',
                      },
                      {
                        text: 'Single',
                        value: 'SINGLE',
                      },
                      {
                        text: 'Married, filing jointly',
                        value: 'MARRIED_JOINT',
                      },
                      {
                        text: 'Married, filing separately',
                        value: 'MARRIED_SEPARATE',
                      },
                      {
                        text: 'Head of household',
                        value: 'HEAD',
                      },
                      {
                        text: 'Widow',
                        value: 'WIDOW',
                      },
                    ],
                    initial: filing_status,
                  },
                },
              ],
            },
          ]}
        />
      );
    } else {
      return (
        <p>
          Loading...
        </p>
      );
    }
  }
}

StatusOnboarding.propTypes = {
  nextPage: PropTypes.string.isRequired,
  nextPageAlt: PropTypes.string.isRequired,
  returnId: PropTypes.string,
};

StatusOnboarding.defaultProps = {
  returnId: null,
};
