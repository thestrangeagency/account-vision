import React from 'react';
import PropTypes from 'prop-types';

import OnboardingForm from '../onboarding-form';
import OnboardingApiService from '../../services/onboarding-api-service';

export default class SpouseOnboarding extends React.Component {
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
    this.getSpouseInfo();
  }

  getSpouseInfo() {
    const { spouseId } = this.props;

    OnboardingApiService.getSpouseInfo(spouseId)
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
      spouseId,
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
          action={OnboardingApiService.updateSpouse}
          nextPage={() => nextPage}
          steps={[
            {
              inputs: [
                {
                  type: 'TEXT',
                  inputProps: {
                    label: "Spouse's First Name",
                    name: 'first_name',
                    required: true,
                    initial: first_name,
                  },
                },
                {
                  type: 'TEXT',
                  inputProps: {
                    label: "Spouse's Last Name",
                    name: 'last_name',
                    required: true,
                    initial: last_name,
                  },
                },
                {
                  type: 'TEXT',
                  inputProps: {
                    label: "Spouse's Middle Name",
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
                    label: "Spouse's Date of birth",
                    name: 'dob',
                    placeholder: 'MM/DD/YYYY',
                    required: true,
                    initial: dob,
                  },
                },
                {
                  type: 'SSN',
                  inputProps: {
                    label: "Spouse's Social security number",
                    name: 'ssn',
                    placeholder: '123456789',
                    required: true,
                    initial: ssn,
                  },
                },
              ],
            },
          ]}
          userId={spouseId}
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

SpouseOnboarding.propTypes = {
  nextPage: PropTypes.string.isRequired,
  spouseId: PropTypes.string.isRequired,
};
