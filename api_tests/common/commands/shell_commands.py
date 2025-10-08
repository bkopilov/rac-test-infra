import logging

import subprocess

from datetime import datetime

logger = logging.getLogger(__name__)


def run_shell_command(cmd, shell=True):
    logger.info(f"run_shell_command {cmd}")
    try:
        process = subprocess.run(cmd, shell=shell, stdout=subprocess.PIPE, universal_newlines=True)
        output = process.stdout.strip()
        logging.info(f'\n {datetime.now()}|>>>\n{output}\n---')
        return output
    except subprocess.CalledProcessError as e:
        logger.error(e)
        return None
