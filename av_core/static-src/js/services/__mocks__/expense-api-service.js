export default class ExpenseApiService {
  static getCommonExpenses() {
    return new Promise((resolve) => {
      process.nextTick(() => {
        resolve({
          expenses: [],
          expensesId: null,
        });
      });
    });
  }
}
