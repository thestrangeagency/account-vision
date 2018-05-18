import React from 'react';
import { shallow } from 'enzyme';

import DeleteConfirmationModal from './delete-confirmation-modal';

test('it renders', () => {
  const wrapper = shallow(<DeleteConfirmationModal onClickConfirm={() => {}} />);
  expect(wrapper).toMatchSnapshot();

  wrapper.setProps({ isActionDisabled: true });
  expect(wrapper).toMatchSnapshot();
});

test('it calls the confirm function prop', () => {
  const onClickConfirm = jest.fn();
  const wrapper = shallow(<DeleteConfirmationModal onClickConfirm={onClickConfirm} />);
  wrapper.find('.btn-danger').simulate('click');
  expect(onClickConfirm).toHaveBeenCalled();
});
