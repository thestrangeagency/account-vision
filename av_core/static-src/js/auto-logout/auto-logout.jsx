import React from 'react';

import { Modal } from '../bootstrap/bootstrap';

const ACTIVITY_TIME_LIMIT = 9 * 60 * 1000;
const COUNTDOWN_TIME_LIMIT = 60 * 1000;
const LOGOUT_URL = '/account/logout';

export default class AutoLogout extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      timeLeft: COUNTDOWN_TIME_LIMIT,
    };

    this.onActivity = this.onActivity.bind(this);
    this.onActivityTimeout = this.onActivityTimeout.bind(this);
    this.onCountdownTick = this.onCountdownTick.bind(this);
    this.onModalHidden = this.onModalHidden.bind(this);
    this.setModalRef = this.setModalRef.bind(this);
  }

  componentDidMount() {
    document.body.addEventListener('mousemove', this.onActivity);
    document.body.addEventListener('keyup', this.onActivity);
    window.addEventListener('scroll', this.onActivity);

    this.restartActivityTimer();
  }

  componentWillUnmount() {
    document.body.removeEventListener('mousemove', this.onActivity);
    document.body.removeEventListener('keyup', this.onActivity);
    window.removeEventListener('scroll', this.onActivity);
  }

  onActivity() {
    if (this.timeout) {
      this.restartActivityTimer();
    }
  }

  onActivityTimeout() {
    this.timeout = null;
    this.showModal();
    this.startCountdown();
  }

  onCountdownFinished() {
    this.clearCountdown();
    window.location = LOGOUT_URL;
  }

  onCountdownTick() {
    const timeIsUp = this.state.timeLeft === 1000;

    this.setState(prevState => (
      {
        timeLeft: prevState.timeLeft - 1000,
      }
    ));

    if (timeIsUp) {
      this.onCountdownFinished();
    }
  }

  onModalHidden() {
    this.restartActivityTimer();
    this.clearCountdown();
    this.setState({ timeLeft: COUNTDOWN_TIME_LIMIT });
  }

  setModalRef(ref) {
    this.modalEl = ref;
    this.modalEl.addEventListener('hidden.bs.modal', this.onModalHidden);
  }

  clearCountdown() {
    clearInterval(this.interval);
    this.interval = null;
  }

  restartActivityTimer() {
    clearTimeout(this.timeout);

    this.timeout = setTimeout(this.onActivityTimeout, ACTIVITY_TIME_LIMIT);
  }

  startCountdown() {
    this.interval = setInterval(this.onCountdownTick, 1000);
  }

  hideModal() {
    this.modal.hide();
  }

  showModal() {
    // first we close any open modal due to a bug in vanilla bootstrap:
    // https://github.com/thednp/bootstrap.native/issues/147
    const openModalEl = document.querySelector('.modal.show');
    if (openModalEl) {
      const openModal = new Modal(openModalEl);
      openModal.hide();
    }

    if (!this.modal) {
      this.modal = new Modal(this.modalEl);
    }

    this.modal.show();
  }

  render() {
    const { timeLeft } = this.state;

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
            <div className="modal-body">
              <h1>
                Are you still there?
              </h1>
              <p>
                You are about to be signed out due to inactivity.
                Please click below to stay signed in.
              </p>
              <p>
                You will be signed out in {timeLeft / 1000} seconds.
              </p>
            </div>
            <div className="modal-footer justify-content-center">
              <button
                className="btn btn-primary"
                data-dismiss="modal"
                type="submit"
              >
                Stay signed in
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }
}
