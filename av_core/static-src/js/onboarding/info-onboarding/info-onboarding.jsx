import React from 'react';
import PropTypes from 'prop-types';

import OnboardingForm from '../onboarding-form';
import OnboardingApiService from '../../services/onboarding-api-service';

export default class InfoOnboarding extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      first_name: null,
      last_name: null,
      middle_name: null,
      dob: null,
      ssn: null,
      hasFetched: false,
    };
  }

  componentDidMount() {
    this.getUserInfo();
  }

  getUserInfo() {
    const { userId } = this.props;

    OnboardingApiService.getUserInfo(userId)
      .then(({
        first_name, last_name, middle_name, dob, ssn,
      }) => (
        this.setState({
          first_name,
          last_name,
          middle_name,
          dob,
          ssn,
          hasFetched: true,
        })
      ));
  }

  render() {
    const {
      nextPage,
      userId,
    } = this.props;

    const {
      first_name,
      last_name,
      middle_name,
      dob,
      ssn,
      hasFetched,
    } = this.state;

    if (hasFetched) {
      return (
        <OnboardingForm
          action={OnboardingApiService.updateUser}
          nextPage={() => nextPage}
          steps={[
            {
              inputs: [
                {
                  type: 'TEXT',
                  inputProps: {
                    label: 'First Name',
                    name: 'first_name',
                    required: true,
                    initial: first_name,
                  },
                },
                {
                  type: 'TEXT',
                  inputProps: {
                    label: 'Last Name',
                    name: 'last_name',
                    required: true,
                    initial: last_name,
                  },
                },
                {
                  type: 'TEXT',
                  inputProps: {
                    label: 'Middle Name',
                    name: 'middle_name',
                    placeholder: '(optional)',
                    initial: middle_name,
                  },
                },
              ],
            },
            {
              inputs: [
                {
                  type: 'DATE',
                  inputProps: {
                    label: 'Date of birth',
                    name: 'dob',
                    placeholder: 'MM/DD/YYYY',
                    required: true,
                    initial: dob,
                  },
                },
                {
                  type: 'SSN',
                  inputProps: {
                    label: 'Social security number',
                    name: 'ssn',
                    placeholder: '123456789',
                    required: true,
                    initial: ssn,
                  },
                },
              ],
            },
          ]}
          userId={userId}
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

InfoOnboarding.propTypes = {
  nextPage: PropTypes.string.isRequired,
  userId: PropTypes.string.isRequired,
};
