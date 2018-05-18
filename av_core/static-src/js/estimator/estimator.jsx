import React from 'react';

export default class Estimator extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      deductions: 0,
      income: 0,
    };

    this.onChangeDeductions = this.onChangeDeductions.bind(this);
    this.onChangeIncome = this.onChangeIncome.bind(this);
  }

  onChangeDeductions(event) {
    const deductions = event.target.value;
    this.setState({ deductions });
  }

  onChangeIncome(event) {
    const income = event.target.value;
    this.setState({ income });
  }

  render() {
    const { deductions, income } = this.state;
    const total = income - deductions;

    return (
      <div className="card my-5">
        <div className="card-body">
          <h1>Estimator</h1>
          <form>
            <div className="form-group">
              <label
                className="form-control-label"
                htmlFor="income"
              >
                  Income
              </label>
              <input
                className="form-control"
                id="income"
                name="income"
                onChange={this.onChangeIncome}
                placeholder="Income"
                type="text"
              />
            </div>
            <div className="form-group">
              <label
                className="form-control-label"
                htmlFor="deductions"
              >
                  Deductions
              </label>
              <input
                className="form-control"
                id="deductions"
                name="deductions"
                onChange={this.onChangeDeductions}
                placeholder="Deductions"
                type="text"
              />
            </div>
          </form>
          <p>Total: ${total}</p>
        </div>
      </div>
    );
  }
}
