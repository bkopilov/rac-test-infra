import logging

import subprocess

logger = logging.getLogger(__name__)


def run_shell_command(cmd):
    cmd = cmd.split()
    logger.debug(f"run_shell_command {cmd}")
    try:
        subprocess.run(cmd)
    except subprocess.CalledProcessError as e:
        logger.error(e)
