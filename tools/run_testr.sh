#!/usr/bin/env bash

set -o pipefail

TESTRARGS=$1
python3 setup.py testr --testr-args="--subunit $TESTRARGS" | subunit-trace -f
retval=$?
echo -e "\nSlowest Tests:\n"
testr slowest
exit $retval

