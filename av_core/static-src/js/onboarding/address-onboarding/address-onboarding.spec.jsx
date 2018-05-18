import React from 'react';
import { shallow } from 'enzyme';

import AddressOnboarding from './address-onboarding';

jest.mock('../../services/onboarding-api-service');

test('it renders', () => {
  const wrapper = shallow(<AddressOnboarding nextPage="" addressId="" />);
  expect(wrapper).toMatchSnapshot();
});
