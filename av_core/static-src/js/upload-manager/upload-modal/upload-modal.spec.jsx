import React from 'react';
import { shallow } from 'enzyme';

import UploadModal from './upload-modal';

test('it renders', () => {
  const wrapper = shallow(<UploadModal
    isSaveDisabled={false}
    onHidden={() => {}}
    onShown={() => {}}
    onSubmit={() => {}}
    setDescriptionRef={() => {}}
  />);
  expect(wrapper).toMatchSnapshot();
});
