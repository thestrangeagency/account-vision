// e.g. 01/15/1980
export const date = /^^(0[1-9]|1[012])[/](0[1-9]|[12][0-9]|3[01])[/](19|20)\d\d$/;

// e.g. 123456789
export const ssn = /^\d{9}$/;

// e.g. ny, NY, nY
export const state = /^([a-z]|[A-Z]){2}$/i;
