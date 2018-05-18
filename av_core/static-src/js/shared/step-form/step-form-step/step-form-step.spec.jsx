import React from 'react';
import { mount } from 'enzyme';

import StepFormStep from './step-form-step';

describe('StepFormStep', () => {
  let wrapper;
  let callback;

  beforeEach(() => {
    callback = jest.fn();

    const inputs = [
      {
        type: 'TEXT',
        inputProps: {
          label: 'First Name',
          name: 'first_name',
          required: false,
        },
      },
    ];

    wrapper = mount((
      <StepFormStep
        hasNextButton
        id="foo"
        inputs={inputs}
        onClickNext={callback}
        onSetValues={() => {}}
      />
    ));
  });

  test('it renders', () => {
    expect(wrapper).toMatchSnapshot();
  });

  test('it can be focused', () => {
    const input = wrapper.find('input').at(0).instance();
    const spy = jest.spyOn(input, 'focus');
    wrapper.setProps({ isFocused: true });
    expect(spy).toHaveBeenCalled();
  });

  test('it calls callback when user presses enter key', () => {
    const spy = jest.spyOn(wrapper.instance(), 'onAdvance');
    wrapper.find('.step-form-step').simulate('keyup', { which: 13 });
    expect(spy).toHaveBeenCalled();
  });

  test('it checks for validity', () => {
    wrapper.setProps({
      inputProps: [
        {
          type: 'TEXT',
          inputProps: {
            label: 'First Name',
            name: 'first_name',
            required: true,
          },
        },
      ],
    });

    const nextButton = wrapper.find('button');
    nextButton.simulate('click');
    expect(wrapper).toMatchSnapshot();

    const input = wrapper.find('input').at(0).instance();
    input.value = 'foo';
    nextButton.simulate('click');
    expect(wrapper).toMatchSnapshot();
  });
});
