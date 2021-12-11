#!/usr/bin/env bash

# Setup Python
sudo apt install -y python3-pip
sudo apt install build-essential libssl-dev libffi-dev python3-dev

# Setup virtual environment
sudo apt install -y python3-venv
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Setup Postgres
sudo apt install -y postgresql postgresql-contrib
sudo -u postgres createdb elixir
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'x9D42Q8USGAthruU8CxD7vzxXYtmwAku';"
./manage.py migrate

# Static
./manage.py collectstatic