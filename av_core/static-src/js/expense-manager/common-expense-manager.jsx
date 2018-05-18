import React from 'react';
import PropTypes from 'prop-types';

import ExpenseApiService from '../services/expense-api-service';

export default class CommonExpenseManager extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      expenses: [],
      expensesId: null,
      isDirty: false,
      isModified: false,
      isSaving: false,
    };

    this.onChangeInput = this.onChangeInput.bind(this);
    this.onSubmit = this.onSubmit.bind(this);
  }

  componentDidMount() {
    this.getExpenses();
  }

  onChangeInput() {
    if (!this.state.isDirty) {
      this.setState({ isDirty: true });
    }

    if (!this.state.isModified) {
      this.setState({ isModified: true });
    }
  }

  onSubmit(e) {
    e.preventDefault();
    e.stopPropagation();

    const { onSaved, year } = this.props;
    const { expensesId, isModified, isSaving } = this.state;

    if (!isModified || isSaving) {
      if (onSaved) {
        onSaved();
      }

      return;
    }

    this.setState({ isSaving: true });

    ExpenseApiService.saveCommonExpenses(e.target, year, expensesId)
      .then(() => {
        this.setState({ isModified: false, isSaving: false });
        if (onSaved) {
          onSaved();
        }
      })
      .catch(() => {
        // TODO show alert
      });
  }

  getExpenses() {
    const { year } = this.props;

    ExpenseApiService.getCommonExpenses(year)
      .then(({ expenses, expensesId }) => (
        this.setState({ expenses, expensesId })
      ));
  }

  render() {
    const { buttonText, forceButtonEnabled } = this.props;
    const {
      expenses, isDirty, isModified, isSaving,
    } = this.state;

    const {
      frozen,
    } = this.props;

    return (
      <form onSubmit={this.onSubmit}>
        {expenses.map(expense => (
          <div className="form-group row" key={expense.name}>
            <label htmlFor={expense.name} className="col-md-8 col-form-label text-capitalize">
              {expense.displayName}
            </label>
            <div className="input-group col-md-4">
              <div className="input-group-addon">$</div>
              <input
                className="form-control"
                defaultValue={expense.value === '0.00' ? '' : expense.value}
                disabled={isSaving}
                id={expense.name}
                name={expense.name}
                onChange={this.onChangeInput}
                type="number"
                readOnly={frozen}
              />
            </div>
          </div>
        ))}
        { !frozen &&
        <button
          className="btn btn-primary"
          disabled={(!isModified || isSaving) && !forceButtonEnabled}
          type="submit"
        >
          {buttonText}
        </button>
        }
        {isSaving &&
          <small className="ml-3 text-muted">Saving...</small>
        }
        {!isModified && isDirty &&
          <small className="ml-3 text-muted">Saved</small>
        }
      </form>
    );
  }
}

CommonExpenseManager.propTypes = {
  buttonText: PropTypes.string,
  forceButtonEnabled: PropTypes.bool,
  onSaved: PropTypes.func,
  year: PropTypes.string.isRequired,
  frozen: PropTypes.bool.isRequired,
};

CommonExpenseManager.defaultProps = {
  buttonText: 'Save',
  forceButtonEnabled: false,
  onSaved: null,
};
