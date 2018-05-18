import React from 'react';
import PropTypes from 'prop-types';

import OnboardingForm from '../onboarding-form';
import OnboardingApiService from '../../services/onboarding-api-service';

export default class DependentsOnboarding extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      dependents: [],
      hasFetched: false,
    };
    this.onClickDone = this.onClickDone.bind(this);
  }

  componentDidMount() {
    this.getDependentInfo();
  }

  onClickDone() {
    window.location = this.props.nextPage;
  }

  getDependentInfo() {
    const { returnYear } = this.props;

    OnboardingApiService.getDependentInfo(returnYear)
      .then(dependents => (
        this.setState({
          dependents,
          hasFetched: true,
        })
      ));
  }

  render() {
    const { returnYear } = this.props;

    const {
      dependents,
      hasFetched,
    } = this.state;

    if (hasFetched) {
      let dependentsList = '';
      if (dependents && dependents.length > 0) {
        dependentsList = (
          <div>
            You have added the following dependents:
            <ul>
              {dependents.map(dependent =>
                <li key={dependent.id.toString()}>{dependent.first_name} {dependent.first_name}</li>)}
            </ul>
          </div>
        );
      }
      return (
        <div>
          <div>
            {dependentsList}
          </div>
          <OnboardingForm
            action={OnboardingApiService.addDependent}
            nextPage={() => window.location.pathname}
            steps={[
              {
                inputs: [
                  {
                    type: 'BINARY',
                    inputProps: {
                      binaryChoices: [
                        {
                          text: 'Add a dependent',
                        },
                        {
                          onClick: this.onClickDone,
                          text: 'Done adding dependents',
                        },
                      ],
                      label: 'Would you like to add dependents?',
                      name: 'has_dependents',
                    },
                  },
                ],
              },
              {
                inputs: [
                  {
                    type: 'TEXT',
                    inputProps: {
                      label: "Dependent's First Name",
                      name: 'first_name',
                      required: true,
                    },
                  },
                  {
                    type: 'TEXT',
                    inputProps: {
                      label: "Dependent's Last Name",
                      name: 'last_name',
                      required: true,
                    },
                  },
                  {
                    type: 'TEXT',
                    inputProps: {
                      label: "Dependent's Middle Name",
                      name: 'middle_name',
                      placeholder: '(optional)',
                    },
                  },
                ],
              },
              {
                inputs: [
                  {
                    type: 'DATE',
                    inputProps: {
                      label: "Dependent's Date of birth",
                      name: 'dob',
                      placeholder: 'MM/DD/YYYY',
                      required: true,
                    },
                  },
                  {
                    type: 'SSN',
                    inputProps: {
                      label: "Dependent's Social security number",
                      name: 'ssn',
                      placeholder: '123456789',
                      required: true,
                    },
                  },
                ],
              },
              {
                inputs: [
                  {
                    type: 'SELECT',
                    inputProps: {
                      label: 'Relationship',
                      name: 'relationship',
                      required: true,
                      selectChoices: [
                        {
                          text: '---------',
                          value: '',
                        },
                        {
                          text: 'Daughter',
                          value: 'DAUGHTER',
                        },
                        {
                          text: 'Son',
                          value: 'SON',
                        },
                        {
                          text: 'Aunt',
                          value: 'AUNT',
                        },
                        {
                          text: 'Brother',
                          value: 'BROTHER',
                        },
                        {
                          text: 'Foster Child',
                          value: 'FOSTER_CHILD',
                        },
                        {
                          text: 'Grandchild',
                          value: 'GRANDCHILD',
                        },
                        {
                          text: 'Grandparent',
                          value: 'GRANDPARENT',
                        },
                        {
                          text: 'Half Brother',
                          value: 'HALF_BROTHER',
                        },
                        {
                          text: 'Half Sister',
                          value: 'HALF_SISTER',
                        },
                        {
                          text: 'Nephew',
                          value: 'NEPHEW',
                        },
                        {
                          text: 'Niece',
                          value: 'NIECE',
                        },
                        {
                          text: 'None',
                          value: 'NONE',
                        },
                        {
                          text: 'Other',
                          value: 'OTHER',
                        },
                        {
                          text: 'Parent',
                          value: 'PARENT',
                        },
                        {
                          text: 'Sister',
                          value: 'SISTER',
                        },
                        {
                          text: 'Stepbrother',
                          value: 'STEPBROTHER',
                        },
                        {
                          text: 'Stepchild',
                          value: 'STEPCHILD',
                        },
                        {
                          text: 'Stepsister',
                          value: 'STEPSISTER',
                        },
                        {
                          text: 'Uncle',
                          value: 'UNCLE',
                        },
                      ],
                    },
                  },
                ],
              },
            ]}
            userId={returnYear}
          />
        </div>
      );
    } else {
      return (
        <p>
          Loading...
        </p>
      );
    }
  }
}

DependentsOnboarding.propTypes = {
  nextPage: PropTypes.string.isRequired,
  returnYear: PropTypes.string.isRequired,
};
