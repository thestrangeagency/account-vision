export default class OnboardingApiService {
  static getUserInfo() {
    return new Promise((resolve) => {
      process.nextTick(() => {
        resolve({
          expenses: [],
          expensesId: null,
        });
      });
    });
  }
  static getAddressInfo() {
    return new Promise((resolve) => {
      process.nextTick(() => {
        resolve({
          expenses: [],
          expensesId: null,
        });
      });
    });
  }
  static getDependentInfo() {
    return new Promise((resolve) => {
      process.nextTick(() => {
        resolve({
          expenses: [],
          expensesId: null,
        });
      });
    });
  }
  static getSpouseInfo() {
    return new Promise((resolve) => {
      process.nextTick(() => {
        resolve({
          expenses: [],
          expensesId: null,
        });
      });
    });
  }
  static getReturnInfo() {
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
