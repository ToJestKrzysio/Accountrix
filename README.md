# Accountrix
A simple REST API managing accounts and their balances

## Run project
Project can be run using docker, via UV, or using just venv.

#### Run using docker compose (suggested)
```shell
docker compose up --build --no-cache
```

#### Run using UV  (on linux / mac)
```shell
export PYTHONPATH=$(pwd) # Add current location to python path, required for absolute imports
uv sync
uv run fastapi run src/main.py --host 127.0.01 --port 8000
```

#### Run using Venv (on linux / mac)
```shell
export PYTHONPATH=$(pwd) # Add current location to python path, required for absolute imports
python -m .venv
source .venv/bin/activate
fastapi run src/main.py --host 127.0.0.1 --port 8000
```

## Overview
After launching the project Rest API should be reachable locally on port [8000](http://127.0.0.1:8000/api/v1/health/), 
for information about specific endpoints refer to swagger [API documentation](http://127.0.0.1:8000/docs) 

## Repo structure
├── src
│   ├── main.py (entrypoint to application)
│   ├── common (Code shared between applications)
│   │   └── schema.py (Schemas used by REST API)
│   ├── accounts (Application handling accounts)
│   │   ├── models.py (Model used to store data, useful when using databases)
│   │   ├── routes.py (Layer handling REST API communication)
│   │   ├── schema.py (Schemas used by REST API)
│   │   └── services.py (Business logic, useful if multiple means of communication with API would be necessary)
│   └── health (Health check application)
└── tests (Tests for the application)

## Requirements
Account should have following information: `id`, `username`, `balance`
- [ ] Endpoint to list all accounts
- [ ] Endpoint to get details for specific account by it's id
- [ ] Endpoint to create new account
- [ ] Endpoint to update specific account by it's id
- [ ] Endpoint to delete specific account by it's id