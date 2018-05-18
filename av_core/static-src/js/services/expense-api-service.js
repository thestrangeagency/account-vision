import Cookies from 'js-cookie';

import { checkStatus } from '../utils';

export default class ExpenseApiService {
  static getCommonUrl(year, id) {
    return `/api/returns/${year}/expenses/common/${id ? `${id}/` : ''}`;
  }

  static getCustomUrl(year, id) {
    return `/api/returns/${year}/expenses/custom/${id ? `${id}/` : ''}`;
  }

  static deleteExpense(year, id) {
    const url = ExpenseApiService.getCustomUrl(year, id);

    return fetch(
      url,
      {
        credentials: 'same-origin',
        headers: {
          'X-CSRFToken': Cookies.get('csrftoken'),
        },
        method: 'delete',
      },
    )
      .then(checkStatus);
  }

  static getCommonExpenses(year) {
    const url = ExpenseApiService.getCommonUrl(year);

    return fetch(
      url,
      {
        credentials: 'same-origin',
      },
    )
      .then(checkStatus)
      .then(response => response.json())
      .then((json) => {
        const jsonBody = json[0];
        const expensesId = jsonBody.id;
        const keys = Object.keys(jsonBody);
        const expenses = keys.filter(key => key !== 'id').map((key) => {
          const displayName = key.replace(/_/g, ' ');
          return { displayName, name: key, value: jsonBody[key] };
        });

        return { expenses, expensesId };
      })
      .catch(ex => console.log('failed to fetch expenses because: ', ex));
  }

  static saveCommonExpenses(form, year, id) {
    const url = ExpenseApiService.getCommonUrl(year, id);

    const formData = new FormData(form);

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
      .then(checkStatus)
      .catch(ex => console.log('failed to fetch expenses because: ', ex));
  }

  static getCustomExpenses(year) {
    const url = ExpenseApiService.getCustomUrl(year);

    return fetch(
      url,
      {
        credentials: 'same-origin',
      },
    )
      .then(checkStatus)
      .then(response => response.json())
      .catch(ex => console.log('failed to fetch expenses because: ', ex));
  }

  static saveExpense({
    amount, id, notes, type,
  }, year) {
    const url = ExpenseApiService.getCustomUrl(year, id);
    const method = id ? 'PATCH' : 'POST';

    const formData = new FormData();
    formData.append('amount', amount);
    formData.append('notes', notes);
    formData.append('type', type);

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
      .then(checkStatus)
      .then(response => response.json());
  }
}
