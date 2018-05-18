import React from 'react';
import { shallow } from 'enzyme';

import UploadsOnboarding from './uploads-onboarding';

test('it renders', () => {
  const wrapper = shallow(<UploadsOnboarding nextPage="" returnYear="" />);
  expect(wrapper).toMatchSnapshot();
});
