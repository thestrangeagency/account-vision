import React from 'react';
import PropTypes from 'prop-types';

import { Modal } from '../../bootstrap/bootstrap';

export default class DeleteConfirmationModal extends React.Component {
  constructor(props) {
    super(props);

    this.setModalRef = this.setModalRef.bind(this);
  }

  setModalRef(ref) {
    this.modalEl = ref;
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
    const { isActionDisabled, onClickConfirm } = this.props;

    return (
      <div
        aria-hidden="true"
        className="modal fade"
        id="confirmDeleteModal"
        ref={this.setModalRef}
        role="dialog"
        tabIndex="-1"
      >
        <div className="modal-dialog">
          <div className="modal-content">
            <div className="modal-body">
              <h5>Are you sure?</h5>
            </div>
            <div className="modal-footer">
              <button
                className="btn btn-secondary"
                data-dismiss="modal"
                disabled={isActionDisabled}
                type="button"
              >
                Cancel
              </button>
              <button
                className="btn btn-danger"
                disabled={isActionDisabled}
                onClick={onClickConfirm}
                type="button"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

DeleteConfirmationModal.propTypes = {
  isActionDisabled: PropTypes.bool,
  onClickConfirm: PropTypes.func.isRequired,
};

DeleteConfirmationModal.defaultProps = {
  isActionDisabled: false,
};
