import React from 'react';
import { shallow } from 'enzyme';

import CommonExpenseManager from './common-expense-manager';

jest.mock('../services/expense-api-service');

test('it renders', () => {
  const wrapper = shallow(<CommonExpenseManager year="2017" />);
  expect(wrapper).toMatchSnapshot();
});
