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
        dot accessible dictionary with all required values for build and test stages
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
    container_name = f"{project_name}_{project_version}"
    # - model/vectorizer name (required for the build process)
    model_name = config.vectorizer.model_name
    # - parameters for uvicorn (runs application)
    host = config.app.host
    port = config.app.port

    # in order to run docker container need to know:
    # - inference container name
    # - test container name
    inference_container_name = f"{container_name}_{config.inference.docker.container.postfix}"
    test_container_name = f"{container_name}_{config.test.docker.container.postfix}"

    return SimpleNamespace(
        **{
            "image_name": image_name,
            "model_name": model_name,
            "host": host,
            "port": port,
            "inference_container_name": inference_container_name,
            "test_container_name": test_container_name,
        },
    )


def start_container(image_name: str, container_name: str, port: int, detach: bool) -> None:
    """Start container with provided name.

    Parameters
    ----------
    image_name: str
        image to use in order to start container
    container_name : str
        container to start
    port: int
        port to map container
    detach: bool
        if True, container will be started in detached mode
    """
    logger.info("Spinning up image `{}` ...".format(container_name))
    subprocess.run(
        f"docker run -it --rm {'--detach' if detach else ''} "
        f"--name {container_name} "
        f"-p {port}:{port} "
        f"{image_name}".split(),
        check=True,
    )
    if detach:
        logger.info("Container is running in detached mode.")


def stop_container(container_name: str) -> None:
    """Stops container with provided name.

    Parameters
    ----------
    container_name : str
        container to stop
    """
    logger.info("Stopping running container `{}` ...".format(container_name))
    try:
        subprocess.run(
            f"docker stop {container_name}".split(),
            check=True,
        )
        logger.info("Container is stopped.")
    except Exception:
        logger.error(
            "Problem with stopping container `{}`. "
            "Perhaps there is no container with such a name.".format(
                container_name,
            ),
        )


# ----------------------------------- STAGES -----------------------------------


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


def inference(detach: bool) -> None:
    """Runs pre-build docker image with name and version parsed from pyproject.toml file.

    Parameters
    ----------
    detach : bool
        in detached model container will be running in background
    """
    config = __create_config()
    start_container(config.image_name, config.inference_container_name, config.port, detach)


def stop_inference_container() -> None:
    """Stops running container."""
    config = __create_config()
    stop_container(config.inference_container_name)


def test() -> None:
    """Starts docker container, runs Docker tests and stops container."""
    config = __create_config()

    try:
        start_container(config.image_name, config.test_container_name, config.port, detach=True)
        logger.info("Starting tests ...")
        pytest.main(["-m", "Docker"])

    finally:
        stop_container(config.test_container_name)


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
        "During `inference` stage the docker image will be started "
        "with the name and version parsed from `pyproject.toml` file; "
        "During `test` stage docker container will be started and docker related tests will be executed."
    )
    stages = {"build": build, "inference": inference, "stop-inference": stop_inference_container, "test": test}
    parser.add_argument("--stage", "-s", type=str, help=help_string, choices=list(stages), required=True)
    parser.add_argument("--detach", "-d", action="store_true", help="Should container be running in detached mode")
    args = parser.parse_args()
    if args.stage == "inference":
        stages[args.stage](args.detach)
    else:
        stages[args.stage]()


if __name__ == "__main__":
    main()
