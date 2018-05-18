import React from 'react';
import { shallow } from 'enzyme';

import StatusOnboarding from './status-onboarding';

jest.mock('../../services/onboarding-api-service');

test('it renders', () => {
  const wrapper = shallow(<StatusOnboarding nextPage="" nextPageAlt="" />);
  expect(wrapper).toMatchSnapshot();
});
