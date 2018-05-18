export function checkStatus(response) {
  if (response.ok) {
    return response;
  }

  return response.json().then((json) => {
    const generalError = json.error || json.detail;

    const error = generalError
      ? { generalError }
      : { validationError: json };

    return Promise.reject(error);
  });
}

export function getFormattedDate(dateString) {
  const date = new Date(dateString);
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const year = date.getFullYear();
  return `${month}/${day}/${year}`;
}

export function bytesToSize(bytes) {
  const sizes = ['bytes', 'kb', 'mb', 'gb', 'tb'];

  if (bytes === 0) {
    return '0 Bytes';
  }

  const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));

  return `${Math.round(bytes / (1024 ** i), 2)} ${sizes[i]}`;
}

// expects value of format MM/DD/YYYY
// returns string of format YYYY-MM-DD
export function formatDateInput(value) {
  const values = value.split('/');
  return `${values[2]}-${values[0]}-${values[1]}`;
}

// opposite of above
export function formatDateOutput(value) {
  if (!value) return null;
  const values = value.split('-');
  return `${values[1]}/${values[2]}/${values[0]}`;
}

export function objectToFormData(object) {
  const formData = new FormData();

  Object.keys(object).forEach((key) => {
    formData.append(key, object[key]);
  });

  return formData;
}
