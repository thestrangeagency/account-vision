import React from 'react';
import { shallow } from 'enzyme';

import OnboardingForm from './onboarding-form';

test('it renders', () => {
  const wrapper = shallow((
    <OnboardingForm
      action={() => {}}
      nextPage={() => {}}
      userId=""
    />
  ));

  expect(wrapper).toMatchSnapshot();
});
