#!/usr/bin/env bash

flake8 .
if [ $?  == "0" ];
then
    pytest -vv --cov=. --cov-report=term-missing --cov-branch --cov-fail-under=98 .
fi