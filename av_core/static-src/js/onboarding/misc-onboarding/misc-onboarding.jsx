import React from 'react';
import PropTypes from 'prop-types';

import OnboardingForm from '../onboarding-form';
import OnboardingApiService from '../../services/onboarding-api-service';

export default class MiscOnboarding extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      county: null,
      has_health: null,
      is_dependent: null,
      is_first_time: null,
      hasFetched: false,
    };
  }

  componentDidMount() {
    this.getReturnInfo();
  }

  getReturnInfo() {
    const { returnId } = this.props;

    OnboardingApiService.getReturnInfo(returnId)
      .then(({
        county, has_health, is_dependent, is_first_time,
      }) => (
        this.setState({
          county,
          has_health,
          is_dependent,
          is_first_time,
          hasFetched: true,
        })
      ));
  }

  render() {
    const {
      nextPage,
      returnId,
    } = this.props;

    const {
      county,
      has_health,
      is_dependent,
      is_first_time,
      hasFetched,
    } = this.state;

    if (hasFetched) {
      return (
        <OnboardingForm
          action={OnboardingApiService.updateReturn}
          nextPage={() => nextPage}
          steps={[
            {
              inputs: [
                {
                  type: 'TEXT',
                  inputProps: {
                    label: 'County',
                    name: 'county',
                    required: false,
                    initial: county,
                  },
                },
              ],
            },
            {
              inputs: [
                {
                  type: 'BINARY',
                  inputProps: {
                    label: 'Do you have health insurance?',
                    name: 'has_health',
                    required: true,
                    initial: has_health === null ? null : has_health.toString(),
                  },
                },
              ],
            },
            {
              inputs: [
                {
                  type: 'BINARY',
                  inputProps: {
                    label: 'Are you a dependant of another?',
                    name: 'is_dependent',
                    required: true,
                    initial: is_dependent === null ? null : is_dependent.toString(),
                  },
                },
              ],
            },
            {
              inputs: [
                {
                  type: 'BINARY',
                  inputProps: {
                    label: 'Is this your first time filing a tax return?',
                    name: 'is_first_time',
                    required: true,
                    initial: is_first_time === null ? null : is_first_time.toString(),
                  },
                },
              ],
            },
          ]}
          userId={returnId}
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

MiscOnboarding.propTypes = {
  nextPage: PropTypes.string.isRequired,
  returnId: PropTypes.string.isRequired,
};
