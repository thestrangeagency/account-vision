import React from 'react';
import { shallow } from 'enzyme';

import ProgressBar from './progress-bar';

test('it renders', () => {
  const wrapper = shallow(<ProgressBar />);
  expect(wrapper).toMatchSnapshot();

  wrapper.setProps({ progress: 0.5 });
  expect(wrapper).toMatchSnapshot();

  wrapper.setProps({ progress: 10 });
  expect(wrapper).toMatchSnapshot();

  wrapper.setProps({ progress: -1 });
  expect(wrapper).toMatchSnapshot();
});
