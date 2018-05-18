import React from 'react';
import PropTypes from 'prop-types';

import OnboardingForm from '../onboarding-form';
import OnboardingApiService from '../../services/onboarding-api-service';
import states from '../../utils/states';

export default class AddressOnboarding extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      address1: null,
      address2: null,
      city: null,
      state: null,
      zip: null,
      hasFetched: false,
    };
  }

  componentDidMount() {
    this.getAddressInfo();
  }

  getAddressInfo() {
    const { addressId } = this.props;

    OnboardingApiService.getAddressInfo(addressId)
      .then(({
        address1, address2, city, state, zip,
      }) => (
        this.setState({
          address1,
          address2,
          city,
          state,
          zip,
          hasFetched: true,
        })
      ));
  }

  render() {
    const {
      nextPage,
      addressId,
    } = this.props;

    const {
      address1,
      address2,
      city,
      state,
      zip,
      hasFetched,
    } = this.state;

    if (hasFetched) {
      return (
        <OnboardingForm
          action={OnboardingApiService.updateAddress}
          nextPage={() => nextPage}
          steps={[
            {
              inputs: [
                {
                  type: 'TEXT',
                  inputProps: {
                    label: 'Street Address',
                    name: 'address1',
                    placeholder: 'Street and number',
                    required: true,
                    initial: address1,
                  },
                },
                {
                  type: 'TEXT',
                  inputProps: {
                    label: 'Street Address Line 2',
                    name: 'address2',
                    placeholder: 'Apartment, suite, unit, building, floor, etc',
                    initial: address2,
                  },
                },
              ],
            },
            {
              inputs: [
                {
                  type: 'TEXT',
                  inputProps: {
                    label: 'City',
                    name: 'city',
                    required: true,
                    initial: city,
                  },
                },
                {
                  type: 'SELECT',
                  inputProps: {
                    label: 'State',
                    name: 'state',
                    required: true,
                    selectChoices: [
                      {
                        text: '---------',
                        value: '',
                      },
                      ...states,
                    ],
                    initial: state,
                  },
                },
                {
                  type: 'TEXT',
                  inputProps: {
                    label: 'Zip Code',
                    name: 'zip',
                    required: true,
                    initial: zip,
                  },
                },
              ],
            },
          ]}
          userId={addressId}
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

AddressOnboarding.propTypes = {
  addressId: PropTypes.string.isRequired,
  nextPage: PropTypes.string.isRequired,
};
