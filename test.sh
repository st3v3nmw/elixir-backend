#!/usr/bin/env bash

flake8 apps elixir
if [ $?  == "0" ];
then
    pytest --cov=apps --cov-report=term-missing --cov-branch --cov-fail-under=100 .
fi