import React from 'react';
import PropTypes from 'prop-types';
import cx from 'classnames';

import { Modal } from '../bootstrap/bootstrap';

export default class ExpenseModal extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      wasValidated: false,
    };

    this.onHidden = this.onHidden.bind(this);
    this.setModalRef = this.setModalRef.bind(this);
    this.onShown = this.onShown.bind(this);
    this.onSubmit = this.onSubmit.bind(this);
  }

  onHidden() {
    this.props.onHidden();
    this.setState({ wasValidated: false });
  }

  onShown() {
    this.props.onShown();
  }

  onSubmit(e) {
    e.preventDefault();
    e.stopPropagation();

    const { onSubmit } = this.props;

    if (this.formEl.checkValidity() === true) {
      onSubmit();
      this.setState({ wasValidated: false });
    } else {
      this.setState({ wasValidated: true });
    }
  }

  setModalRef(ref) {
    this.modalEl = ref;
    this.modalEl.addEventListener('hidden.bs.modal', this.onHidden);
    this.modalEl.addEventListener('shown.bs.modal', this.onShown);
  }

  /*
  public method
  */
  hide() {
    this.modal.hide();
  }

  /*
  public method
  */
  show() {
    if (!this.modal) {
      this.modal = new Modal(this.modalEl);
    }

    this.modal.show();
  }

  render() {
    const {
      expense,
      generalError,
      isSaveDisabled,
      setAmountRef,
      setNotesRef,
      setTypeRef,
      validationError,
    } = this.props;

    const { wasValidated } = this.state;

    return (
      <div
        aria-hidden="true"
        className="modal fade"
        ref={this.setModalRef}
        role="dialog"
        tabIndex="-1"
      >
        <div className="modal-dialog">
          <div className="modal-content">
            <form
              className={cx('m-0', {
                'was-validated': wasValidated,
              })}
              noValidate
              onSubmit={this.onSubmit}
              ref={(ref) => { this.formEl = ref; }}
            >
              <div className="modal-body">
                <div className="form-row">
                  <div className="form-group col-md-8">
                    <label htmlFor="input_type">
                      Expense Type
                    </label>
                    <input
                      className={cx('form-control', {
                        'is-invalid': validationError && validationError.type,
                      })}
                      id="input_type"
                      maxLength="32"
                      name="type"
                      ref={setTypeRef}
                      required
                      type="text"
                    />
                    {validationError && validationError.type &&
                      <div className="invalid-feedback">
                        {validationError.type.map(error => (
                          <p className="mb-1" key={error}>{error}</p>
                        ))}
                      </div>
                    }
                  </div>
                  <div className="form-group col-md-4">
                    <label htmlFor="input_amount">
                      Amount
                    </label>
                    <div className="input-group">
                      <div className="input-group-addon">$</div>
                      <input
                        className={cx('form-control', {
                          'is-invalid': validationError && validationError.amount,
                        })}
                        id="input_amount"
                        name="amount"
                        ref={setAmountRef}
                        required
                        type="number"
                        min="0.00"
                        step="0.01"
                      />
                    </div>
                    {validationError && validationError.amount &&
                      <div className="invalid-feedback">
                        <p>{validationError.amount[0]}</p>
                        <p>{validationError.amount[0]}</p>
                      </div>
                    }
                  </div>
                </div>
                <div className="form-group">
                  <label htmlFor="input_notes">
                    Notes
                  </label>
                  <textarea
                    className={cx('form-control', {
                      'is-invalid': validationError && validationError.notes,
                    })}
                    id="input_notes"
                    name="notes"
                    ref={setNotesRef}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button
                  className="btn btn-secondary"
                  data-dismiss="modal"
                  disabled={isSaveDisabled}
                  type="button"
                >
                  Cancel
                </button>
                <button
                  className="btn btn-primary"
                  disabled={isSaveDisabled}
                  type="submit"
                >
                  {expense ? 'Update' : 'Add'}
                </button>
              </div>
              {generalError &&
                <div className="alert alert-danger mx-3" role="alert">
                  {generalError}
                </div>
              }
            </form>
          </div>
        </div>
      </div>
    );
  }
}

ExpenseModal.propTypes = {
  expense: PropTypes.shape({}),
  generalError: PropTypes.string,
  isSaveDisabled: PropTypes.bool,
  onHidden: PropTypes.func.isRequired,
  onShown: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  setAmountRef: PropTypes.func.isRequired,
  setNotesRef: PropTypes.func.isRequired,
  setTypeRef: PropTypes.func.isRequired,
  validationError: PropTypes.shape({}),
};

ExpenseModal.defaultProps = {
  expense: null,
  generalError: null,
  isSaveDisabled: false,
  validationError: null,
};
