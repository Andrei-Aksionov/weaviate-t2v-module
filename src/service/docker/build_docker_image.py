import subprocess

import toml
import yaml


def main() -> None:
    """Helper function to build docker image without providing arguments.

    Parse parameters from config files and call `docker build` with them
    as arguments for the build procedure.
    """
    # parsing project's metadata and config files
    project_metadata = toml.load("pyproject.toml")
    with open("src/config/config.yaml", "r") as fin:
        config = yaml.safe_load(fin)

    # in order to build docker image need to know:
    # - name and version (for docker tag)
    # - model/vectorizer name (required for the build process)
    name = project_metadata["tool"]["poetry"]["name"]
    version = project_metadata["tool"]["poetry"]["version"]
    model_name = config["vectorizer"]["model_name"]
    # - parameters for uvicorn (runs application)
    host = config["app"]["host"]
    port = config["app"]["port"]

    subprocess.run(
        "docker build "
        "--file src/service/docker/Dockerfile . "
        f"--tag {name}:{version} "
        f"--build-arg MODEL_NAME={model_name} "
        f"--build-arg HOST={host} "
        f"--build-arg PORT={port}".split(),
        check=True,
    )


if __name__ == "__main__":
    main()
