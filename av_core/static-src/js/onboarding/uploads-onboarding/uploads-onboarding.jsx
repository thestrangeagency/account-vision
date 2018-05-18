import React from 'react';
import PropTypes from 'prop-types';

import UploadManager from '../../upload-manager/upload-manager';

export default function CommonOnboarding({ nextPage, returnYear }) {
  function onClickNext() {
    window.location = nextPage;
  }

  return (
    <div className="custom-onboarding">
      <div className="row">
        <div className="col">
          <p>The list provided below are some examples of forms that you can upload.
            Feel free to upload any additional forms you feel our CPAs might need to see.
            If you have a copy of your tax return from the previous year,
            please upload that as well.
          </p>
          <ul>
            <li>W-2</li>
            <li>1099-INT: Interest Income</li>
            <li>1099-DIV: Dividends and Distributions</li>
            <li>1098, Mortgage Interest Statement,</li>
            <li>1098-E, Student Loan Interest Statement</li>
            <li>1099-B: Proceeds from Broker and Barter Exchange Transactions</li>
            <li>1099-MISC: Miscellaneous Income</li>
            <li>State Drivers License</li>
          </ul>
          <UploadManager year={returnYear} />
        </div>
      </div>
      <div className="row justify-content-center">
        <div className="col col-6">
          <button
            className="btn btn-primary w-100"
            onClick={onClickNext}
            type="button"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}

CommonOnboarding.propTypes = {
  nextPage: PropTypes.string.isRequired,
  returnYear: PropTypes.string.isRequired,
};
