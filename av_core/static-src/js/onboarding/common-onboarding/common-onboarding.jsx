import React from 'react';
import PropTypes from 'prop-types';

import CommonExpenseManager from '../../expense-manager/common-expense-manager';

export default function CommonOnboarding({ nextPage, returnYear }) {
  function onClickNext() {
    window.location = nextPage;
  }

  return (
    <div className="common-onboarding">
      <div className="row">
        <div className="col">
          <h4 className="my-3">Do you have any of these expenses?</h4>
          <CommonExpenseManager
            buttonText="Next"
            forceButtonEnabled
            onSaved={onClickNext}
            year={returnYear}
          />
        </div>
      </div>
    </div>
  );
}

CommonOnboarding.propTypes = {
  nextPage: PropTypes.string.isRequired,
  returnYear: PropTypes.string.isRequired,
};
