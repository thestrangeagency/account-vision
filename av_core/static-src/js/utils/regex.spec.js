import { date, ssn, state } from './regex';

test('it checks a date', () => {
  expect(date.test('10.01.2017')).toBeFalsy();
  expect(date.test('10-01-2017')).toBeFalsy();
  expect(date.test('10012017')).toBeFalsy();
  expect(date.test('10-1-2017')).toBeFalsy();
  expect(date.test('10/1/2017')).toBeFalsy();
  expect(date.test('10/01/17')).toBeFalsy();
  expect(date.test('10/01/20177')).toBeFalsy();
  expect(date.test('110/01/2017')).toBeFalsy();
  expect(date.test('10/01/2017')).toBeTruthy();
});

test('it checks a ssn', () => {
  expect(ssn.test('abc')).toBeFalsy();
  expect(ssn.test('111')).toBeFalsy();
  expect(ssn.test('111-11-1111')).toBeFalsy();
  expect(ssn.test('1234567')).toBeFalsy();
  expect(ssn.test('1234567891')).toBeFalsy();
  expect(ssn.test('123456789')).toBeTruthy();
});

test('it checks a state', () => {
  expect(state.test('n')).toBeFalsy();
  expect(state.test('nyy')).toBeFalsy();
  expect(state.test('N')).toBeFalsy();
  expect(state.test('NYY')).toBeFalsy();
  expect(state.test('ny')).toBeTruthy();
  expect(state.test('NY')).toBeTruthy();
  expect(state.test('Ny')).toBeTruthy();
});
