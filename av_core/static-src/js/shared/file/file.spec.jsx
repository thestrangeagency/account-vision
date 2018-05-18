import React from 'react';
import { shallow } from 'enzyme';

import File from './file';

const onClickDelete = jest.fn();
const onClickEdit = jest.fn();

const fileProps = {
  date: '10/28/2017',
  name: 'my-file.txt',
  onClickDelete,
  onClickEdit,
  size: '200kb',
  type: 'txt',
};

const wrapper = shallow(<File {...fileProps} />);

test('it renders', () => {
  expect(wrapper).toMatchSnapshot();
});

test('it calls remove callback', () => {
  wrapper.find('[aria-label="Remove"]').simulate('click');
  expect(onClickDelete).toHaveBeenCalled();
});

test('it calls edit callback', () => {
  wrapper.find('[aria-label="Edit"]').simulate('click');
  expect(onClickEdit).toHaveBeenCalled();
});
