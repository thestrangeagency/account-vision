#!/bin/bash

# release phase commands for all apps

python manage.py migrate
python manage.py loaddata av_core/fixtures/flatpages.json
