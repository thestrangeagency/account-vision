import React from 'react';
import ReactDOM from 'react-dom';
import 'whatwg-fetch';

import './bootstrap/bootstrap';
import AutoLogout from './auto-logout/auto-logout';
import Estimator from './estimator/estimator';
import CommonExpenseManager from './expense-manager/common-expense-manager';
import CustomExpenseManager from './expense-manager/custom-expense-manager';
import UploadManager from './upload-manager/upload-manager';
import InfoOnboarding from './onboarding/info-onboarding/info-onboarding';
import StatusOnboarding from './onboarding/status-onboarding/status-onboarding';
import SpouseOnboarding from './onboarding/spouse-onboarding/spouse-onboarding';
import AddressOnboarding from './onboarding/address-onboarding/address-onboarding';
import DependentsOnboarding from './onboarding/dependents-onboarding/dependents-onboarding';
import MiscOnboarding from './onboarding/misc-onboarding/misc-onboarding';
import CommonOnboarding from './onboarding/common-onboarding/common-onboarding';
import CustomOnboarding from './onboarding/custom-onboarding/custom-onboarding';
import UploadsOnboarding from './onboarding/uploads-onboarding/uploads-onboarding';

const components = [
  {
    attributes: {},
    componentClass: AutoLogout,
    id: 'auto-logout',
  },
  {
    attributes: {},
    componentClass: Estimator,
    id: 'estimator',
  },
  {
    attributes: {
      'data-year': 'year',
      'data-frozen': 'frozen',
    },
    componentClass: CommonExpenseManager,
    id: 'common-expense-manager',
  },
  {
    attributes: {
      'data-year': 'year',
      'data-frozen': 'frozen',
    },
    componentClass: CustomExpenseManager,
    id: 'custom-expense-manager',
  },
  {
    attributes: {
      'data-year': 'year',
      'data-target': 'target',
      'data-frozen': 'frozen',
    },
    componentClass: UploadManager,
    id: 'upload-manager',
  },
  {
    attributes: {
      'data-user': 'userId',
      'data-next-page': 'nextPage',
    },
    componentClass: InfoOnboarding,
    id: 'info-onboarding',
  },
  {
    attributes: {
      'data-next-page': 'nextPage',
      'data-next-page-alt': 'nextPageAlt',
      'data-return-id': 'returnId',
    },
    componentClass: StatusOnboarding,
    id: 'status-onboarding',
  },
  {
    attributes: {
      'data-next-page': 'nextPage',
      'data-spouse-id': 'spouseId',
    },
    componentClass: SpouseOnboarding,
    id: 'spouse-onboarding',
  },
  {
    attributes: {
      'data-address-id': 'addressId',
      'data-next-page': 'nextPage',
    },
    componentClass: AddressOnboarding,
    id: 'address-onboarding',
  },
  {
    attributes: {
      'data-next-page': 'nextPage',
      'data-return-year': 'returnYear',
    },
    componentClass: DependentsOnboarding,
    id: 'dependents-onboarding',
  },
  {
    attributes: {
      'data-next-page': 'nextPage',
      'data-return-id': 'returnId',
    },
    componentClass: MiscOnboarding,
    id: 'misc-onboarding',
  },
  {
    attributes: {
      'data-next-page': 'nextPage',
      'data-return-year': 'returnYear',
    },
    componentClass: CommonOnboarding,
    id: 'on-common-expenses-onboarding',
  },
  {
    attributes: {
      'data-next-page': 'nextPage',
      'data-return-year': 'returnYear',
    },
    componentClass: CustomOnboarding,
    id: 'on-custom-expenses-onboarding',
  },
  {
    attributes: {
      'data-next-page': 'nextPage',
      'data-return-year': 'returnYear',
    },
    componentClass: UploadsOnboarding,
    id: 'on-uploads-onboarding',
  },
];

components.forEach((component) => {
  const { attributes, componentClass, id } = component;
  const el = document.getElementById(id);

  if (el) {
    const Component = componentClass;
    const props = {};

    Object.keys(attributes).forEach((key) => {
      props[attributes[key]] = el.getAttribute(key);
    });

    ReactDOM.render(<Component {...props} />, el);
  }
});
