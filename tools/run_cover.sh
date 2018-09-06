#!/usr/bin/env bash

TESTRARGS=$1
python setup.py testr --coverage --testr-args="$TESTRARGS"
retval=$?
coverage report -m
exit $retval
