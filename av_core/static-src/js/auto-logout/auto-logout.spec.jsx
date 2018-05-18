import React from 'react';
import { shallow } from 'enzyme';

import AutoLogout from './auto-logout';

test('it renders', () => {
  const wrapper = shallow(<AutoLogout />);
  expect(wrapper).toMatchSnapshot();
});
