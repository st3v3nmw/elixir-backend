#!/usr/bin/env bash

flake8 apps elixir
if [ $?  == "0" ];
then
    coverage run --source='apps' manage.py test
    coverage report -m
fi