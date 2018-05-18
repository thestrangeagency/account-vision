import React from 'react';
import PropTypes from 'prop-types';

import CustomExpenseManager from '../../expense-manager/custom-expense-manager';

export default function CommonOnboarding({ nextPage, returnYear }) {
  function onClickNext() {
    window.location = nextPage;
  }

  function onClickBack() {
    window.location = '/welcome/common/';
  }

  return (
    <div className="custom-onboarding">
      <div className="row">
        <div className="col mb-3">
          <h4 className="my-3">Do you have any custom expenses you’d like to enter?</h4>
          <p>Do you have any other expenses that you would like to enter that were not listed on the previous page?</p>
          <CustomExpenseManager year={returnYear} />
        </div>
      </div>
      <div className="row">
        <div className="col">
          <p className="mb-3">
            If you are done adding expenses or prefer to add them later, click NEXT to continue.
          </p>
        </div>
      </div>
      <div className="row">
        <div className="col col-6 mr-auto">
          <button
            className="tx-anchor-button"
            onClick={onClickBack}
            type="button"
          >
            ← Back
          </button>
        </div>
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
