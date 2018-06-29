# Account Vision


## Local Development

### Make sure you have [homebrew](https://brew.sh/) installed and added to your path
```sh
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

### Make sure you have python 3.6 installed
```sh
brew install python3
```

### Make sure you have pipenv installed using pip3
```sh
pip3 install --user pipenv
```

### Make sure pipenv is in your path
Run `python3 -m site --user-base` to find your user base binary directory. Add `bin` to the end and add this to your path, e.g.:
```
export PATH=~/Library/Python/3.6/bin:$PATH
```

### Clone the repo and install dependencies

```sh
git clone git@github.com:thestrangeagency/account-vision.git
cd account-vision

# install python dependencies
pipenv install

# install npm packages
npm install
```

### Stripe setup

__Note: this is global, across all installations. You probably DO NOT need to do this.__

Delete all test data first using the [dashboard](https://dashboard.stripe.com/account/data), and then set up a product and pricing.

```
# load a product and pricing plans
python manage.py shell < av_utils/create_plans.py
```

### Start the local server

```sh
# enter the virtualenv
pipenv shell

# build js and css
npm run postinstall

# update db tables and collect static files
python manage.py migrate
python manage.py collectstatic

# use heroku dev server
heroku local

# or use django dev server
python manage.py runserver

# or use werkzeug for debugging
python manage.py runserver_plus
```

Note: if you want to use the heroku dev server, you'll need the heroku cli:
```
brew install heroku/brew/heroku
```

### Build JS and CSS

To watch css and js files for changes, run the following commands in separate terminal windows:

```sh
# watch and compile js
npm start
```

```sh
# watch and compile sass
npm run sass:watch
```

Additional commands:

```sh
# build js
npm run build

# build sass
npm run sass

# build js and sass
npm run postinstall
```

### Adding Bootstrap JS components

We are using (Native JavaScript for Bootstrap)[http://thednp.github.io/bootstrap.native/] for Bootstrap components that rely on JavaScript. Components can be integrated into the project on a case by case basis. To add a new component, first download the (archive)[https://github.com/thednp/bootstrap.native/archive/master.zip]. Then, from the downloaded folder, export an individual module:

```sh
npm i
node build-v4.js --only <module_name> >> <destination_file>
```

Take the newly created .js file and move it to `av_core/static/js/bootstrap`, and import it for use in `av_core/static/js/app.js` like so:

```
import Collapse from './bootstrap/collapse';
```

## Testing

```sh
python manage.py test

npm test

# fix snapshots
npm test -- -u
```

## Deployment

Commits to master automatically deploy to dev.

Heroku runs release phase items in `release.sh`, migrating the database and collecting static assets.

View release output like so:

```sh
heroku releases
heroku releases:output v10
```

## Fixtures

Review apps will load some fixture data automatically:

users:
* admin: admin@a.com / a
* cpa: cpa@a.com / a


```sh
# clean local database
python manage.py flush

# load dev fixtures 
./review.sh

# fixtures can be installed remotely like this
heroku run python manage.py loaddata account/fixtures/users.json -a acvi-stage-pr-13

```

```
# to dump group data, we want natural keys
python manage.py dumpdata auth --natural-foreign --natural-primary --indent 4 -e auth.Permission
```

## Cron jobs

Use Heroku Scheduler to run the following:

```
python manage.py stripe
python manage.py purge_streams
# this one needs updating:
# python manage.py abandoned
```


## Heroku Shell

Ideally not needed, but:

```sh
heroku run bash -a acvi-stage
```

## Manual Push

```sh
git push heroku master
heroku run python manage.py migrate
heroku run python manage.py collectstatic
```

## Pre-commit Hook

The project uses an npm module called Husky to run a pre-commit hook, which is specified in `package.json`. To commit without running the hook, run:

```sh
git commit -m <commit_message> --no-verify
```
