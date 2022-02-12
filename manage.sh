#!/bin/bash

if [ "$1" == "test" ]; then
    docker run -it --net=elixir-backend_services_network elixir-backend_web flake8 .
    if [ $?  == "0" ]; then
        docker run -it --net=elixir-backend_services_network elixir-backend_web\
            pytest -vv --cov=. --cov-report=term-missing --cov-branch --cov-fail-under=98 .
    fi
elif [ "$1" == "bash" ]; then
    docker exec -it "$2" bash
else
    docker run -it --net=elixir-backend_services_network elixir-backend_web\
        python3.10 manage.py "$@"
fi