import React from 'react';
import PropTypes from 'prop-types';

import ExpenseApiService from '../services/expense-api-service';
import ExpenseModal from './expense-modal';
import DeleteConfirmationModal from '../shared/delete-confirmation-modal/delete-confirmation-modal';

export default class CustomExpenseManager extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      expenses: null,
      focusedExpenseIndex: null, // the expense that an edit or delete modal targets
      generalError: null,
      isConfirmDeleteDisabled: false,
      isSaveDisabled: false,
      validationError: null,
    };

    this.onClickAdd = this.onClickAdd.bind(this);
    this.onClickDeleteConfirm = this.onClickDeleteConfirm.bind(this);
    this.onExpenseModalHidden = this.onExpenseModalHidden.bind(this);
    this.onExpenseModalShown = this.onExpenseModalShown.bind(this);
    this.onSubmit = this.onSubmit.bind(this);
  }

  componentDidMount() {
    this.getExpenses();
  }

  onExpenseModalHidden() {
    this.setState({
      focusedExpenseIndex: null,
      generalError: null,
      validationError: null,
    });
  }

  onExpenseModalShown() {
    this.inputExpenseTypeEl.focus();
  }

  onClickAdd() {
    this.inputExpenseAmountEl.value = '';
    this.inputExpenseNotesEl.value = '';
    this.inputExpenseTypeEl.value = '';

    this.expenseModalEl.show();
  }

  onClickDelete(expenseIndex) {
    this.setState({ focusedExpenseIndex: expenseIndex }, () => {
      this.confirmDeleteModalEl.show();
    });
  }

  onClickDeleteConfirm() {
    const { year } = this.props;
    const { expenses, focusedExpenseIndex } = this.state;
    const focusedExpense = expenses[focusedExpenseIndex];

    this.setState({ isConfirmDeleteDisabled: true });

    ExpenseApiService.deleteExpense(year, focusedExpense.id)
      .then(() => {
        this.setState({
          expenses: [
            ...expenses.slice(0, focusedExpenseIndex),
            ...expenses.slice(focusedExpenseIndex + 1),
          ],
          focusedExpenseIndex: null,
          isConfirmDeleteDisabled: false,
        });

        this.confirmDeleteModalEl.hide();

        this.getExpenses();
      })
      .catch(() => {
        this.setState({ isConfirmDeleteDisabled: false });
        console.log('failed to delete expense ', focusedExpense.id);
      });
  }

  onClickEdit(expenseIndex) {
    this.setState({ focusedExpenseIndex: expenseIndex }, () => {
      const { expenses } = this.state;
      const expense = expenses[expenseIndex];

      this.inputExpenseAmountEl.value = expense.amount;
      this.inputExpenseNotesEl.value = expense.notes;
      this.inputExpenseTypeEl.value = expense.type;

      this.expenseModalEl.show();
    });
  }

  onSubmit() {
    const amount = this.inputExpenseAmountEl.value;
    const notes = this.inputExpenseNotesEl.value;
    const type = this.inputExpenseTypeEl.value;

    const { year } = this.props;
    const { expenses, focusedExpenseIndex } = this.state;
    const focusedExpense = expenses[focusedExpenseIndex];

    const id = focusedExpense && focusedExpense.id;

    this.setState({ isSaveDisabled: true });

    ExpenseApiService.saveExpense({
      amount, id, notes, type,
    }, year)
      .then((expense) => {
        // if we're editing an expense, replace it in the expenses array
        // with the new expense, otherwise push the new expense to the array
        const newExpenses = focusedExpenseIndex !== null
          ? [
            ...expenses.slice(0, focusedExpenseIndex),
            expense,
            ...expenses.slice(focusedExpenseIndex + 1),
          ]
          : [...expenses, expense];

        this.setState({
          expenses: newExpenses,
          isSaveDisabled: false,
        });
        this.expenseModalEl.hide();
      })
      .catch((ex) => {
        const { generalError, validationError } = ex;

        this.setState({
          generalError,
          isSaveDisabled: false,
          validationError,
        });
      });
  }

  getExpenses() {
    const { year } = this.props;

    ExpenseApiService.getCustomExpenses(year)
      .then(expenses => this.setState({ expenses }));
  }

  render() {
    const {
      expenses,
      focusedExpenseIndex,
      generalError,
      isConfirmDeleteDisabled,
      isSaveDisabled,
      validationError,
    } = this.state;
    const focusedExpense = focusedExpenseIndex !== null ? expenses[focusedExpenseIndex] : null;
    const {
      frozen,
    } = this.props;

    const iconSize = 48;

    return (
      <div>
        {expenses && expenses.length === 0 && !frozen &&
          <p>Looks like you don&apos;t have any custom expenses yet. Click below to add one.</p>
        }
        {expenses && expenses.length > 0 &&
          <ul className="list-group mb-4">
            {expenses.map((expense, index) => (
              <li className="list-group-item" key={expense.id}>
                <div className="row">
                  <span className="col-4 d-flex align-items-center">
                    {expense.type}
                    {expense.notes && !frozen &&
                      <span className="">
                        <button
                          className="expense-manager__expense__button"
                          onClick={() => this.onClickEdit(index)}
                          type="button"
                        >
                          <img src="/static/svg/icon_note.svg" width={iconSize} height={iconSize} alt="note" />
                        </button>
                      </span>
                    }
                  </span>
                  <span className="col-4 d-flex align-items-center justify-content-end px-0">${expense.amount}</span>
                  {!frozen &&
                  <span className="col-4 text-right text-nowrap px-0">
                    <button
                      className="expense-manager__expense__button"
                      onClick={() => this.onClickEdit(index)}
                      type="button"
                    >
                      <img src="/static/svg/icon_edit.svg" width={iconSize} height={iconSize} alt="edit" />
                    </button>
                    <button
                      className="expense-manager__expense__button"
                      onClick={() => this.onClickDelete(index)}
                      type="button"
                    >
                      <img src="/static/svg/icon_delete.svg" width={iconSize} height={iconSize} alt="delete" />
                    </button>
                  </span>
                  }
                </div>
              </li>
            ))}
          </ul>
        }
        {!frozen &&
        <button
          className="btn btn-primary"
          onClick={this.onClickAdd}
          type="button"
        >
          Add
        </button>
        }
        <ExpenseModal
          expense={focusedExpense}
          generalError={generalError}
          isSaveDisabled={isSaveDisabled}
          onHidden={this.onExpenseModalHidden}
          onShown={this.onExpenseModalShown}
          onSubmit={this.onSubmit}
          ref={(ref) => { this.expenseModalEl = ref; }}
          setAmountRef={(ref) => { this.inputExpenseAmountEl = ref; }}
          setNotesRef={(ref) => { this.inputExpenseNotesEl = ref; }}
          setTypeRef={(ref) => { this.inputExpenseTypeEl = ref; }}
          validationError={validationError}
        />
        <DeleteConfirmationModal
          isActionDisabled={isConfirmDeleteDisabled}
          onClickConfirm={this.onClickDeleteConfirm}
          ref={(ref) => { this.confirmDeleteModalEl = ref; }}
        />
      </div>
    );
  }
}

CustomExpenseManager.propTypes = {
  year: PropTypes.string.isRequired,
  frozen: PropTypes.bool.isRequired,
};
