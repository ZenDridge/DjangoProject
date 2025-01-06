!1/bin/bash

# install dependancies
pip install setuptools
pip install -r requirements.txt

# django commands
python manage.py makemigrations
python manage.py migrate
python manage.py tailwind install
python manage.py collectstatic
python manage.py tailwind start