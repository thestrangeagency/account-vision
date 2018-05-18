import React from 'react';
import { shallow } from 'enzyme';

import DependentsOnboarding from './dependents-onboarding';

jest.mock('../../services/onboarding-api-service');

test('it renders', () => {
  const wrapper = shallow(<DependentsOnboarding nextPage="" returnYear="" />);
  expect(wrapper).toMatchSnapshot();

  wrapper.setState({ choseYes: true });
  expect(wrapper).toMatchSnapshot();
});
