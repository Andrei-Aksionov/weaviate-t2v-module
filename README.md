<h1 align="center">Welcome to weaviate-t2v-module</h1>

<p align=center><img src="references/readme/images/similarity.jpg"></p>

> Service that takes text as an input and returns it's vector representation. Texts with similar meaning will have similar vectors, texts with different meaning - different vectors.

This project was created as a replacement of the Weaviate's default text2vec-transformers module in order to use custom vectorization model ([sentence-transformer](https://github.com/UKPLab/sentence-transformers) pretrained model is used in this repo).

In order to create custom text2vec-transformers module these 4 endpoints have to be implemented (as it's described in [official documentation](https://weaviate.io/developers/weaviate/current/modules/custom-modules.html)):

- GET /.well-known/live -> respond 204 when the app is alive
- GET /.well-known/ready -> respond 204 when the app is ready to serve traffic
- GET /meta -> respond meta information about the inference model
- POST /vectors -> respond vector representation of the text

Though this module is created for Weaviate it can be used for any other purpose where text vectorization is required. Just use `/vectors` endpoint for it.
</p>

## How to use different model

Currently [msmarco-distilbert-base-v4](https://www.sbert.net/docs/pretrained-models/msmarco-v3.html) is used as it's better suited for text vector search. It's an asymmetric model which is better for my needs. More about difference between symmetric/asymmetric models you can find [here](msmarco-distilbert-base-v4).

If you want to use any other pretrained model from [the list](https://www.sbert.net/docs/pretrained_models.html) then just change the model name in the **src/config/config.yaml** file.

In case of any other model then these three changes have to be made:

- **src/utils/meta.py** - change the way dictionary with model's meta info is generated
- **src/features/vectorizer.py** - adapt vectorization process to the new model
- **app.py** - instantiate new model

## Install

As this project uses pyproject.toml - [poetry](https://python-poetry.org/docs/) has to be installed.

Also take a look at the required python version (described in **pyproject.toml** file).

In order to install all required packages run this command (when you are in the folder with pyproject.toml file).

```sh
poetry install
```

## Usage

In order to run this service just start it with uvicorn:

```sh
python -m uvicorn app:app --port 8080
```

## Docker

In order to build docker image there is a helper script: **src/service/docker/manage.py**. It expects an argument **--stage** with one of this values:

- build
- test

In order to build docker image with name and version that are parsed from *pyproject.toml* file simply run:

```sh
python src/service/docker/manage.py --stage build
```

After image is built it can be started with:

```sh
docker run -it --rm -p 8080:8080 weaviate-t2-module:[version]
```

**Examples of api calls can be found in src/service/api_calls.rest file.**

## Run tests

[Pytest](https://github.com/pytest-dev/pytest) framework is used for tests execution so in order to run all tests simply type:

```sh
pytest
```

It will run all tests including tests for docker container. If you want to run all tests except for docker ones:

```sh
pytest -m "not Docker"
```

And if you want to run only docker container tests (container has to be running):

```sh
pytest -m "Docker"
```

It's also possible to start docker container and run tests in one command:

```sh
python src/service/docker/manage.py --stage test
```

The command above will start docker container, run tests and stop it.

***

For tests [Hypothesis](https://hypothesis.readthedocs.io/en/latest/) is used. It will try to generate many different variants of passing variables in order to check all cases (including edge ones).

In order to see statistics of variable generation run:

```sh
pytest --hypothesis-show-statistics
```

If you want to see what variables were generated run:

```sh
pytest -s --hypothesis-verbosity=debug
```
