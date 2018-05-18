import React from 'react';
import { shallow } from 'enzyme';

import InfoOnboarding from './info-onboarding';

jest.mock('../../services/onboarding-api-service');

test('it renders', () => {
  const wrapper = shallow(<InfoOnboarding nextPage="" userId="" />);
  expect(wrapper).toMatchSnapshot();
});
