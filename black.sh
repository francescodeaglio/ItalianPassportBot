
black availability_handler/*
isort availability_handler/*
black bot
isort bot/*
black databases/*
isort databases/*
black poller/*
isort poller/*
black queues/*
isort queues/*
black telegram_dispatcher/*
isort telegram_dispatcher/*
black user_handler/*
isort user_handler/*



echo "Running auto-formatters"

mamba run -n modyn isort . > /dev/null
mamba run -n modyn autopep8 modyn integrationtests --recursive --in-place --pep8-passes 2000 > /dev/null
mamba run -n modyn black modyn integrationtests --verbose --config black.toml > /dev/null

echo "Running linters"

if mamba run -n modyn flake8 modyn ; then
    echo "No flake8 errors"
else
    echo "flake8 errors"
    exit 1
fi

if mamba run -n modyn isort . --check --diff ; then
    echo "No isort errors"
else
    echo "isort errors"
    exit 1
fi

if mamba run -n modyn black --check modyn --config black.toml ; then
    echo "No black errors"
else
    echo "black errors"
    exit 1
fi

if mamba run -n modyn pylint modyn ; then
    echo "No pylint errors"
else
    echo "pylint errors"
    exit 1
fi

echo "Running tests"

if mamba run -n modyn pytest ; then
    echo "No pytest errors"
else
    echo "pytest errors"
    exit 1
fi

if mamba run -n modyn mypy modyn ; then
    echo "No mypy errors"
else
    echo "mypy errors"
    exit 1
fi

echo "Successful compliance check"

popd