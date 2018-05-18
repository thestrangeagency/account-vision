import React from 'react';
import { shallow } from 'enzyme';

import DateInput from './date-input';

describe('DateInput', () => {
  let wrapper;
  let input;

  beforeEach(() => {
    wrapper = shallow((
      <DateInput
        id="date"
        name="date"
        placeholder="enter date here"
        required
      />
    ));

    input = wrapper.find('input');
  });

  test('it renders', () => {
    expect(wrapper).toMatchSnapshot();
  });

  test('it validates the date format', () => {
    const pattern = input.prop('pattern');
    const regex = new RegExp(pattern);
    expect(regex.test('10-01-2017')).toBeFalsy();
    expect(regex.test('10012017')).toBeFalsy();
    expect(regex.test('10-1-2017')).toBeFalsy();
    expect(regex.test('10/1/2017')).toBeFalsy();
    expect(regex.test('10/01/17')).toBeFalsy();
    expect(regex.test('10/01/20177')).toBeFalsy();
    expect(regex.test('110/01/2017')).toBeFalsy();
    expect(regex.test('10/01/2017')).toBeTruthy();
  });
});
