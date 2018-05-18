import Cookies from 'js-cookie';

import { checkStatus, objectToFormData } from '../utils';

export default class OnboardingApiService {
  static getUserInfo(userId) {
    const url = `/api/users/${userId}/`;

    return fetch(
      url,
      {
        credentials: 'same-origin',
      },
    )
      .then(checkStatus)
      .then(response => response.json())
      .catch(ex => console.log('failed to fetch user because: ', ex));
  }

  static getDependentInfo(year) {
    const url = `/api/returns/${year}/dependents/`;

    return fetch(
      url,
      {
        credentials: 'same-origin',
      },
    )
      .then(checkStatus)
      .then(response => response.json())
      .catch(ex => console.log('failed to fetch dependents because: ', ex));
  }

  static addDependent(formValues, year) {
    const url = `/api/returns/${year}/dependents/`;
    const formData = objectToFormData(formValues);

    return fetch(
      url,
      {
        body: formData,
        credentials: 'same-origin',
        headers: {
          'X-CSRFToken': Cookies.get('csrftoken'),
        },
        method: 'POST',
      },
    )
      .then(checkStatus);
  }

  static getAddressInfo(addressId) {
    const url = `/api/address/${addressId ? `${addressId}/` : ''}`;

    return fetch(
      url,
      {
        credentials: 'same-origin',
      },
    )
      .then(checkStatus)
      .then(response => response.json())
      .catch(ex => console.log('failed to fetch address because: ', ex));
  }

  static updateAddress(formValues, addressId) {
    const url = `/api/address/${addressId ? `${addressId}/` : ''}`;
    const method = addressId ? 'PATCH' : 'POST';
    const formData = objectToFormData(formValues);

    return fetch(
      url,
      {
        body: formData,
        credentials: 'same-origin',
        headers: {
          'X-CSRFToken': Cookies.get('csrftoken'),
        },
        method,
      },
    )
      .then(checkStatus);
  }

  static getSpouseInfo(spouseId) {
    const url = `/api/spouse/${spouseId}/`;

    return fetch(
      url,
      {
        credentials: 'same-origin',
      },
    )
      .then(checkStatus)
      .then(response => response.json())
      .catch(ex => console.log('failed to fetch spouse because: ', ex));
  }

  static updateSpouse(formValues, spouseId) {
    const url = `/api/spouse/${spouseId}/`;
    const formData = objectToFormData(formValues);

    return fetch(
      url,
      {
        body: formData,
        credentials: 'same-origin',
        headers: {
          'X-CSRFToken': Cookies.get('csrftoken'),
        },
        method: 'PATCH',
      },
    )
      .then(checkStatus);
  }

  static updateUser(formValues, userId) {
    const url = `/api/users/${userId}/`;
    const formData = objectToFormData(formValues);

    return fetch(
      url,
      {
        body: formData,
        credentials: 'same-origin',
        headers: {
          'X-CSRFToken': Cookies.get('csrftoken'),
        },
        method: 'PATCH',
      },
    )
      .then(checkStatus);
  }

  static createReturn(formValues) {
    const url = '/api/returns/';
    const formData = objectToFormData(formValues);

    return fetch(
      url,
      {
        body: formData,
        credentials: 'same-origin',
        headers: {
          'X-CSRFToken': Cookies.get('csrftoken'),
        },
        method: 'POST',
      },
    )
      .then(checkStatus);
  }

  static getReturnInfo(returnId) {
    const url = `/api/returns/${returnId}/`;

    return fetch(
      url,
      {
        credentials: 'same-origin',
      },
    )
      .then(checkStatus)
      .then(response => response.json())
      .catch(ex => console.log('failed to fetch return because: ', ex));
  }

  static updateReturn(formValues, returnId) {
    const url = `/api/returns/${returnId}/`;
    const formData = objectToFormData(formValues);

    return fetch(
      url,
      {
        body: formData,
        credentials: 'same-origin',
        headers: {
          'X-CSRFToken': Cookies.get('csrftoken'),
        },
        method: 'PATCH',
      },
    )
      .then(checkStatus);
  }
}
