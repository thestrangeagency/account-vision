#!/bin/bash

# post deploy commands for review apps

python manage.py migrate
python manage.py loaddata av_core/fixtures/groups.json
python manage.py loaddata av_account/fixtures/questions.json
