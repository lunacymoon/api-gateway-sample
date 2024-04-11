# ECIP API GATEWAY

This is an example of API Gateway for micro-services implemented in Python with FastAPI stack.

<br></br>

## Installation

1. Clone project

   ```sh
   $ git clone https://OrcaApps@dev.azure.com/OrcaApps/ECIP/_git/ecip-api-gateway
   ```

2. Install `poetry` and setup user

   ```sh
   $ pip install poetry
   ```

3. Install project dependencies with poetry

   ```sh
   $ poetry install
   ```

4. install `pre-commit` and `pre-push`

   ```sh
   $ pre-commit install
   $ pre-commit install --hook-type pre-push
   ```

## Run ECIP API Gateway

- with `VSCode`

  ```
  Activity Bar --> Run and Debug -->  Start Debugging `Python: ECIP API Gateway`
  ```

- with `uvicorn` command

  ```sh
  $ uvicorn main:app \
      --port 8010 \
      --app-dir ./src \
      --log-config ./src/settings/logging_conf.yaml \
      [OPTIONS]
  ```

## Run test cases

- with `VSCode`

  ```
  Activity Bar --> Run and Debug -->  Start Debugging `Python: Testing`
  ```

- with `pytest` command

  ```sh
  $ TEST=true pytest --cache-clear --log-level=ERROR -W=error -sxvv

  # test a module
  $ [ENVIRONMENTS] pytest [OPTIONS] src/.../aaa

  # test a file
  $ [ENVIRONMENTS] pytest [OPTIONS] src/.../aaa/bbb.py

  # test a function
  $ [ENVIRONMENTS] pytest [OPTIONS] src/.../aaa/bbb.py::ccc
  ```