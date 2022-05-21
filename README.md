# Elixir Backend

The frontend's [here](https://github.com/st3v3nmw/elixir-frontend).

## Setup

1. Fresh install?, run `scripts/setup.sh` to install the required packages like Docker.
2. Deploy/build docker container
3. Run `python manage.py migrate`.
4. `python manage.py runscript populate_coding_tables`
5. Get into `web` container, 
6. In the container, run the following commands to generate JWT keys:
    1. `ssh-keygen -t rsa -P "" -b 4096 -m PEM -f jwtRS384.key`
    2. `ssh-keygen -e -m PEM -f jwtRS384.key > jwtRS384.key.pub`

## Deploying to Remote

1. Setup passwordless SSH on remote.
2. On the remote machine, run the `scripts/setup.sh` script (if 1st deploy).
3. Create context for remote: `docker context create remote --docker "host=ssh://user@ip"`
4. Change docker context: `docker context use remote`
5. Deploy: `COMPOSE_DOCKER_CLI_BUILD=0 docker-compose up -d --build`
6. Confirm that containers are up & running: `docker ps` (`docker-compose logs -f` to check logs)
