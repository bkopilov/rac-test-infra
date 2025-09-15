import logging

import subprocess

logger = logging.getLogger(__name__)


def run_shell_command(cmd, shell=True):
    logger.info(f"run_shell_command {cmd}")
    try:
        process = subprocess.run(cmd, shell=shell, stdout=subprocess.PIPE, universal_newlines=True)
        output = process.stdout.strip()
        return output
    except subprocess.CalledProcessError as e:
        logger.error(e)
        return None
