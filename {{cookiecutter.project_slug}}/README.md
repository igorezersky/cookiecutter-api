# {{ cookiecutter.project_name }}

## Overview

ASGI RESTful API by [igorezersky/cookiecutter-api](https://github.com/igorezersky/cookiecutter-api)

## Requirements

Make sure that all requirements related for your platform will be installed before main package installation.

### Linux | Windows | macOS

### Docker

Normally, to build project image you will need to install following packages:

- [Python](https://python.org/downloads)

- [Docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/)

## Installation

### Linux | Windows | macOS

Following instructions are guidelines, you can install it differently, however,
executing the following commands will ensure that `{{ cookiecutter.project_slug }}` is installed correctly:

Clone repository and create [virtual environment](https://docs.python.org/3/library/venv.html):

```console
foo@bar:~$ cd {{ cookiecutter.project_slug }}
foo@bar:~/{{ cookiecutter.project_slug }}$ python -m venv venv && source venv/bin/activate
foo@bar:~/{{ cookiecutter.project_slug }}$ python -m pip install --upgrade pip wheel setuptools
```

Install requirements:

```console
foo@bar:~/{{ cookiecutter.project_slug }}$ pip install -r requirements/dev.txt
```

### Docker

Make sure that you have execution permissions for `docker`, `docker-compose`, `python` and `pydeployhelp`.

Use `pydeployhelp` package to build project image:

```console
foo@bar:~/{{ cookiecutter.project_slug }}$ pydeployhelp
Enter deploy tasks from following: all | build up down: build
        ✓ processing deploy tasks: build
Enter deploy targets from following: all | {{ cookiecutter.project_slug }}-db {{ cookiecutter.project_slug }}-backend: all
        ✓ processing deploy targets: {{ cookiecutter.project_slug }}-db {{ cookiecutter.project_slug }}-backend
Do you agree to start processing (yes or no)? [yes]: yes
```

## Environment

Create `.env` file in project root with environment variables:

```text
ENV=dev
PROJECT_NAME={{ cookiecutter.project_slug }}
SECRET_KEY=skey
HOST=localhost
PORT=8080
ENABLE_CORS=True
DB_HOST=localhost
DB_PORT=5432
DB_NAME={{ cookiecutter.project_slug }}
DB_USERNAME=admin
DB_PASSWORD=admin
VOLUMES_ROOT={{ cookiecutter.volumes_path }}
```

What does each variable mean:

* `ENV`: environment type (dev, prod), could contain any value, but for production please set `ENV=prod`

* `PROJECT_NAME`: this name will be used for docker containers creation

* `SECRET_KEY`: this key will be used for passwords hashing (should be securely stored)

* `HOST`: backend host (e.g. localhost, project.dns.com)

* `PORT`: backend port, will be ignored when `ENV=prod`

* `ENABLE_CORS`: if True, all origins and methods will be allowed

* `DB_HOST`: database host (e.g. localhost), will be ignored when using docker

* `DB_PORT`: database port (e.g. 5432)

* `DB_NAME`: database name (e.g. {{ cookiecutter.project_slug }})

* `DB_USERNAME`: database admin username (should be securely stored)

* `DB_PASSWORD`: database admin password (should be securely stored)

* `VOLUMES_ROOT`: path to directory, where docker volumes will be stored; it's highly recommended to set this value to the path of the project root (on development machine) - this will allow you to use the same data when debugging from IDE and when deploying via docker (pydeployhelp)

## Usage

### Linux | Windows | macOS

You can manually start project:

```console
foo@bar:~/{{ cookiecutter.project_slug }}$ python run.py
```

### Docker

Use `pydeployhelp` package to run project image:

```console
foo@bar:~/{{ cookiecutter.project_slug }}$ pydeployhelp
Enter deploy tasks from following: all | build up down: up
        ✓ processing deploy tasks: up
Enter deploy targets from following: all | {{ cookiecutter.project_slug }}-db {{ cookiecutter.project_slug }}-backend: all
        ✓ processing deploy targets: {{ cookiecutter.project_slug }}-db {{ cookiecutter.project_slug }}-backend
Do you agree to start processing (yes or no)? [yes]: yes
```
