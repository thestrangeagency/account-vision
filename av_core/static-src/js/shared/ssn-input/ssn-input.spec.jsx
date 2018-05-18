import React from 'react';
import { shallow } from 'enzyme';

import SsnInput from './ssn-input';

test('it renders', () => {
  const wrapper = shallow((
    <SsnInput
      id="date"
      name="date"
      placeholder="enter ssn here"
      required
    />
  ));

  expect(wrapper).toMatchSnapshot();
});
