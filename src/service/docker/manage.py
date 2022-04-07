import argparse
import json
import subprocess
from types import SimpleNamespace

import pytest
import toml
from loguru import logger

from src import config


def __create_config() -> SimpleNamespace:
    """Returns config that is needed for build and test stages.

    Helper function that parses pyproject.toml and src config files
    and return config with parameters that are needed for both build
    and test stages.

    Returns
    -------
    SimpleNamespace
        dot accessable dictionary with all required values for build and test stages
    """
    # parsing project's metadata files into SimpleNamespace object
    # (nested dictionary with dot access)
    project_metadata = json.loads(
        json.dumps(
            toml.load("pyproject.toml"),
        ),
        object_hook=lambda item: SimpleNamespace(**item),
    )

    # in order to build docker image need to know:
    # - name and version (for docker tag)
    project_name = project_metadata.tool.poetry.name
    project_version = project_metadata.tool.poetry.version
    image_name = f"{project_name}:{project_version}"
    # - model/vectorizer name (required for the build process)
    model_name = config.vectorizer.model_name
    # - parameters for uvicorn (runs application)
    host = config.app.host
    port = config.app.port

    # in order to run docker container need to know:
    # - test container name
    test_container_name = f"{project_name}_{project_version}_{config.test.docker.container.postfix}"

    return SimpleNamespace(
        **{
            "image_name": image_name,
            "model_name": model_name,
            "host": host,
            "port": port,
            "test_container_name": test_container_name,
        },
    )


def build() -> None:
    """Builds docker image with name and version that are parsed from pyproject.toml file."""
    config = __create_config()

    logger.info("Starting build image `{}` ...".format(config.image_name))
    subprocess.run(
        "docker build "
        "--file src/service/docker/Dockerfile . "
        f"--tag {config.image_name} "
        f"--build-arg MODEL_NAME={config.model_name} "
        f"--build-arg HOST={config.host} "
        f"--build-arg PORT={config.port}".split(),
        check=True,
    )
    logger.info("Image `{}` is built".format(config.image_name))


def test() -> None:
    """Starts docker container, runs Docker tests and stops container."""
    config = __create_config()

    try:
        logger.info("Starting container `{}` ...".format(config.test_container_name))
        subprocess.run(
            "docker run --rm --detach "
            f"--name {config.test_container_name} "
            f"-p {config.port}:{config.port} "
            f"{config.image_name}".split(),
            check=True,
        )

        logger.info("Starting tests ...")
        pytest.main(["-m", "Docker"])

    finally:
        logger.info("Stopping container `{}` ...".format(config.test_container_name))
        subprocess.run(
            f"docker stop {config.test_container_name}".split(),
            check=True,
        )
        logger.info("Container `{}` is stopped".format(config.test_container_name))


def main() -> None:
    """Main function for managing docker.

    Depending on --stage parameter either docker image will be built or docker container
    will be started, docker related tests will be executed and after that this docker
    container will be stopped.
    """
    parser = argparse.ArgumentParser(description="Script that can either build image or test docker container.")
    help_string = (
        "Name of the operation: either `build` or `test`. "
        "During `build` stage docker image will be built with the name and version parsed from `pyproject.toml` file; "
        "During `test` stage docker container will be started and docker related tests will be executed."
    )
    stages = {"build": build, "test": test}
    parser.add_argument("--stage", "-s", type=str, help=help_string, choices=list(stages), required=True)
    args = parser.parse_args()
    stages[args.stage]()


if __name__ == "__main__":
    main()
