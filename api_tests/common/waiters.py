import logging

import openshift_client as oc
import waiting

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level to DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

OPERATORS_TIMEOUT = 720
OPERATORS_RETRY = 30

def _are_operators_available(**conditions_kwargs):
    """Verify operators are available post cluster installation.

    cmd: oc get clusteroperators
    conditions_kwargs must get the same params as in the cmd results example: status="True", type="Available"
    Will allow us to extend the filtering condition.
    When cluster installation completed, going over the clusters operators list expecting for:
    status: "True"
    type: Available
    """

    def compare_by(cond, **kwargs):
        for key, value in kwargs.items():
            if cond.get(key) != value:
                return False
        return True

    with oc.project("default"):
        try:
            operators = oc.selector("clusteroperators").objects()
            # all operators state is False (not available before checking)
            available_operators = {
                operator.model.metadata.name: False for operator in operators
            }
            for operator in operators:
                for condition in operator.model.status.conditions:
                    if compare_by(condition, **conditions_kwargs):
                        available_operators[operator.model.metadata.name] = True
                        break
            # Check  available operators are in true state
            logger.info(f"Operators: {available_operators}")
            if all(available_operators.values()):
                return True
        except oc.OpenShiftPythonException as e:
            logging.info(
                f"Got an exception while trying to get clusteroperators status. Error: {e}"
            )
        return False

def wait_for_operators_status_ready():
    logger.debug("Checking if All operators are Ready")
    waiting.wait(
        lambda: _are_operators_available(status="True", type="Available"),
        timeout_seconds=OPERATORS_TIMEOUT,
        sleep_seconds=OPERATORS_RETRY,
        waiting_for="All operators cluster to be Ready",
    )