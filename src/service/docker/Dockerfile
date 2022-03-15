############################## GLOBAL ARGUMENTS ##############################
### setting up global arguments that will be used in both build stages ###
ARG APP_DIR=/usr/app
# to use the latest version of poetry use `master` instead of exact numeric version
ARG POETRY_VERSION=1.1.13
# sentence transformer model to load during `docker build`
#   otherwise it will be downloaded each time during `docker run`
ARG MODEL_NAME
# arguments for uvicorn
ARG HOST
ARG PORT

##############################################################################
############################ The first build stage ###########################
##############################################################################

FROM python:3.9-slim-bullseye as base

ARG APP_DIR
ARG POETRY_VERSION

RUN apt-get update; \
    apt-get install curl -y

# installing poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/$POETRY_VERSION/get-poetry.py | python -
ENV PATH="${PATH}:/root/.poetry/bin"

COPY pyproject.toml poetry.lock ./

# creating virtual environment and activating it
RUN python -m venv $APP_DIR/venv
ENV PATH="${APP_DIR}/venv/bin:$PATH"

RUN pip install --upgrade pip; \
    poetry export -f requirements.txt | pip install -r /dev/stdin --no-cache-dir


##############################################################################
############################ The second build stage ##########################
##############################################################################

FROM python:3.9-slim-bullseye

ARG APP_DIR
ARG MODEL_NAME

# retrieving provided args and assigning them to environment variables
# so they can be use during `docker run`
# (args are visible only during `docker build`)
ARG HOST
ENV HOST=${HOST}
ARG PORT
ENV PORT=${PORT}

# creating non-root user
RUN groupadd python --gid 1000; \
    useradd python --gid 1000 --uid 1000 --create-home --shell /bin/false

RUN apt-get update; \
    apt-get upgrade -y; \
    apt-get autoclean

WORKDIR $APP_DIR

# copying venv from previous step and making it permanently activated
COPY --from=base --chown=python:python $APP_DIR/venv $APP_DIR/venv
ENV PATH="${APP_DIR}/venv/bin:$PATH"

USER python

# downloading sentence transformer model during `docker build`
# otherwise it will be downloaded each time during `docker run`
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('${MODEL_NAME}');"

COPY --chown=python:python src/ src/
COPY --chown=python:python app.py .

ENTRYPOINT [ "/bin/sh", "-c"]
CMD ["uvicorn app:app --host ${HOST} --port ${PORT}"]
