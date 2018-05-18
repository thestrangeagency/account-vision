import React from 'react';
import { shallow } from 'enzyme';

import SpouseOnboarding from './spouse-onboarding';

jest.mock('../../services/onboarding-api-service');

test('it renders', () => {
  const wrapper = shallow(<SpouseOnboarding nextPage="" spouseId="" />);
  expect(wrapper).toMatchSnapshot();
});
