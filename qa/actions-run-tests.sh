#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"

pushd "${SCRIPT_DIR}/.." > /dev/null

set -e
set -x

COVERAGE_THRESHOLD=95

export TERM=xterm

# set up terminal colors
RED=$(tput bold && tput setaf 1)
GREEN=$(tput bold && tput setaf 2)
YELLOW=$(tput bold && tput setaf 3)
NORMAL=$(tput sgr0)


echo "Create Virtualenv for Python deps ..."
pip install -U pip
pip install virtualenv
virtualenv --version
virtualenv -p python3 venv && source venv/bin/activate
pip install -r tests/requirements.txt
PYTHONPATH=`pwd` python3 "$(which pytest)" --cov=f8a_utils/ --cov-report term-missing --cov-fail-under=95 -vv tests/
codecov --token=b3420bb6-159c-49d3-8bd2-9cf2727069e8      
printf "%stests passed%s\n\n" "${GREEN}" "${NORMAL}"


popd > /dev/null
