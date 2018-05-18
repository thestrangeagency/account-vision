import React from 'react';
import PropTypes from 'prop-types';
import cx from 'classnames';

import { Modal } from '../../bootstrap/bootstrap';

export default class UploadModal extends React.Component {
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
      isSaveDisabled,
      setDescriptionRef,
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
                <div className="form-group">
                  <label htmlFor="input_description">
                    Description
                  </label>
                  <textarea
                    className="form-control"
                    id="input_description"
                    name="notes"
                    ref={setDescriptionRef}
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
                  Update
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }
}

UploadModal.propTypes = {
  isSaveDisabled: PropTypes.bool,
  onHidden: PropTypes.func.isRequired,
  onShown: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  setDescriptionRef: PropTypes.func.isRequired,
};

UploadModal.defaultProps = {
  isSaveDisabled: false,
};
