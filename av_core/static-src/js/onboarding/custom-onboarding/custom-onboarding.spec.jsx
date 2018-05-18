import React from 'react';
import { shallow } from 'enzyme';

import CustomOnboarding from './custom-onboarding';

test('it renders', () => {
  const wrapper = shallow(<CustomOnboarding nextPage="" returnYear="" />);
  expect(wrapper).toMatchSnapshot();
});
