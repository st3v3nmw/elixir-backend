#!/usr/bin/env bash

flake8 apps utils elixir
if [ $?  == "0" ];
then
    pytest --cov=. --cov-report=term-missing --cov-branch --cov-fail-under=100 .
fi