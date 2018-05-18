import React from 'react';
import { shallow } from 'enzyme';

import UploadManager from './upload-manager';

jest.mock('../services/upload-api-service');

test('it renders', () => {
  const wrapper = shallow(<UploadManager year="2017" />);
  expect(wrapper).toMatchSnapshot();
});
