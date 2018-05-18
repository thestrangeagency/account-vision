import React from 'react';
import { shallow } from 'enzyme';

import MiscOnboarding from './misc-onboarding';

jest.mock('../../services/onboarding-api-service');

test('it renders', () => {
  const wrapper = shallow(<MiscOnboarding nextPage="" returnId="" />);
  expect(wrapper).toMatchSnapshot();
});
