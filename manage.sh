#!/bin/bash

if [ "$1" == "test" ]; then
    docker-compose exec web flake8 .
    if [ $?  == "0" ];
    then
        docker-compose exec web pytest -vv --cov=. --cov-report=term-missing --cov-branch\
            --cov-fail-under=98 .
    fi
else
    docker-compose exec web python3.10 manage.py "$@"
fi