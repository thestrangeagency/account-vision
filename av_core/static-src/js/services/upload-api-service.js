import Cookies from 'js-cookie';

import { checkStatus } from '../utils';

export default class UploadApiService {
  static getFiles(year, target) {
    let filesUrl = `/api/returns/${year}/files/?only_uploaded=1`;
    if (target) {
      filesUrl = `/api/returns/${year}/${target}/files/?only_uploaded=1`;
    }

    return fetch(filesUrl, {
      credentials: 'same-origin',
    })
      .then(checkStatus)
      .then(response => response.json());
  }

  static deleteFile(url) {
    return fetch(url, {
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': Cookies.get('csrftoken'),
      },
      method: 'delete',
    }).then(checkStatus);
  }

  static updateFile(url, description) {
    const formData = new FormData();
    formData.append('description', description);

    return fetch(url, {
      body: formData,
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': Cookies.get('csrftoken'),
      },
      method: 'PATCH',
    })
      .then(checkStatus)
      .then(response => response.json());
  }
}
