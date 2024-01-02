#!/bin/bash

directories=("availability_handler" "bot" "common" "poller" "dispatcher" "user_handler")

for dir in "${directories[@]}"; do
    echo "Processing directory: $dir"

    black $dir/*.py
    isort $dir/*.py
    autopep8 $dir/*.py --in-place --recursive --pep8-passes 2000

    if flake8 $dir/*.py ; then
        echo "No flake8 errors"
    else
        echo "flake8 errors"
    fi

    if isort $dir/*.py --check --diff ; then
        echo "No isort errors"
    else
        echo "isort errors"
        exit 1
    fi


    if mypy $dir/*.py ; then
        echo "No mypy errors"
    else
        echo "mypy errors"
    fi

    echo "Successful compliance check for $dir"

done
