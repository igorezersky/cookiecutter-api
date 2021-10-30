# base image
FROM python:3.9-buster AS builder-image

# add service user
ARG PROJECT_USER
RUN adduser --disabled-password ${PROJECT_USER}
WORKDIR /home/${PROJECT_USER}
USER ${PROJECT_USER}

# create project dir
ARG PROJECT_SLUG
WORKDIR /home/${PROJECT_USER}/${PROJECT_SLUG}

# install requirements
ARG VIRTUAL_ENV
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python -m pip install --upgrade --no-cache-dir pip setuptools wheel
COPY requirements/common.txt common.txt
COPY requirements/prod.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir && rm -rf /var/lib/apt/lists/*

# main image
FROM python:3.9-slim AS main-image

# add service user
ARG PROJECT_USER
RUN adduser --disabled-password ${PROJECT_USER}
WORKDIR /home/${PROJECT_USER}
USER ${PROJECT_USER}

# create project dir
ARG PROJECT_SLUG
WORKDIR /home/${PROJECT_USER}/${PROJECT_SLUG}
RUN mkdir logs

# copy `venv` from builder-image to main-image
ARG VIRTUAL_ENV
COPY --from=builder-image ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# activate virtual env
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# copy project files
COPY LICENSE *.py *.in ./
COPY {{ cookiecutter.project_slug }} {{ cookiecutter.project_slug }}
