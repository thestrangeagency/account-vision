import React from 'react';
import { shallow } from 'enzyme';

import StepForm from './step-form';

test('it renders', () => {
  const wrapper = shallow(<StepForm onSubmit={() => {}} />);
  expect(wrapper).toMatchSnapshot();
});
