#! /bin/env python

import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional

from loguru import logger

SECRET_NAME = "regcred"
NAMESPACE = "default"
DOCKER_SERVER = "ghcr.io"
DOCKER_USERNAME: str = None
DOCKER_PASSWORD: str = None


def _get_stdin_input(help_text: str) -> str:
    return input(f"[{help_text}] > ")


def run_command(command: list[str] | str) -> int:
    if isinstance(command, str):
        command = command.split(" ")

    try:
        return subprocess.run(command).returncode
    except FileNotFoundError:
        logger.error(f"Invalid command provided: {command}")
        sys.exit()
    except Exception as exc:
        logger.error(f"Unexpected error: {exc}")
        sys.exit()


def required_value(
    help_text: str,
    err_message: Optional[str] = None,
    *,
    validator: Optional[Callable] = None,
) -> str:
    if not validator:
        return _get_stdin_input(help_text)

    while True:
        tmp_value = _get_stdin_input(help_text)
        if not validator(tmp_value):
            logger.warning(err_message if err_message else "Invalid input")
            continue

        return tmp_value


if __name__ == "__main__":

    logger.info(f"Log in to {DOCKER_SERVER}")
    DOCKER_USERNAME = required_value(
        "Enter github username",
        "Username is empty",
        validator=lambda x: len(x)
    )
    run_command(["docker", "login", DOCKER_SERVER, "-u", DOCKER_USERNAME])

    logger.info(f"Checking for secret '{SECRET_NAME}'...")
    if not run_command(f"kubectl get secrets {SECRET_NAME} -n {NAMESPACE}"):
        logger.info(f"Secret '{SECRET_NAME}' exists. Deleting it...")

        run_command(f"kubectl delete secret {SECRET_NAME} -n {NAMESPACE}")
    else:
        logger.info(f"Secret '{SECRET_NAME}' does not exist")

    config_path = Path.home() / ".docker/config.json"
    if not config_path.exists():
        logger.error(f"File '{config_path}' is not exist")

        config_path = required_value(
            "Specify path to docker config file",
            "File is not exist",
            validator=lambda x: Path(x).exists()
        )

    logger.info(f"Creating secret '{SECRET_NAME}'...")
    run_command(
        [
            "kubectl", "create", "secret", "generic", SECRET_NAME,
            f"--from-file=.dockerconfigjson={config_path}",
            "--type=kubernetes.io/dockerconfigjson"
        ]
    )

    logger.info("Secret configured")
