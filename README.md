# Elixir Backend

## Setup

1. Fresh install?, run `scripts/install.sh` to install the required packages like Docker.
2. Deploy/build docker container
3. Run `python manage.py migrate`.
4. `python manage.py runscript populate_coding_tables`
5. Get into `web` container, 
6. In the container, run the following commands to generate JWT keys:
    1. `ssh-keygen -t rsa -P "" -b 4096 -m PEM -f jwtRS384.key`
    2. `ssh-keygen -e -m PEM -f jwtRS384.key > jwtRS384.key.pub`

## Random commands

1. `docker-compose up -d --build`
