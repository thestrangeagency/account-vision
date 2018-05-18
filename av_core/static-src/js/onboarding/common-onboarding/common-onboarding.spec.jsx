import React from 'react';
import { shallow } from 'enzyme';

import CommonOnboarding from './common-onboarding';

test('it renders', () => {
  const wrapper = shallow(<CommonOnboarding nextPage="" returnYear="" />);
  expect(wrapper).toMatchSnapshot();
});
