import logging
from retry import retry
import openshift_client as oc

logger = logging.getLogger(__name__)
oc_client = oc
RETRIES = 3
RETRIES_DELAY = 10


@retry(exceptions=RuntimeError, tries=RETRIES, delay=RETRIES_DELAY)
def oc_select(resource, namespace):
    with oc.project(namespace):
        try:
            logger.debug(f"oc_select {resource}' on project '{namespace}'")
            output = oc.selector(resource).objects()
            return output
        except oc.OpenShiftPythonException as e:
            raise RuntimeError(f"Unable to get object {resource} -> {str(e)}")


@retry(exceptions=RuntimeError, tries=RETRIES, delay=RETRIES_DELAY)
def oc_create(str_dict, cmd_args=None, namespace=None):
    # namespace should be detected from yaml.
    with oc.project(namespace):
        try:
            logger.debug(f"oc_create '{str_dict}' on project '{namespace}'")
            output = oc.create(str_dict, cmd_args)
            return output
        except oc.OpenShiftPythonException as e:
            raise RuntimeError(f"Unable to create object {str_dict}: {str(e)}")


def oc_node_interfaces_ip():
    """list of interface with ipv4
    example: [{"name": "eth1", "ipv4": "10.1.1.1/24"},}]
    """
    interfaces_obj = oc_select("nns", "default")
    logger.debug(f"interfaces_obj info: {interfaces_obj}")
    interfaces = interfaces_obj[0].as_dict()['status']['currentState']['interfaces']
    interfaces_list = []
    for interface in interfaces:
        interface_dict = {'name': interface['name']}
        if not (interface.get('ipv4') and interface['ipv4'].get("address")):
            interface_dict['ipv4'] = None
        else:
            address = interface['ipv4'].get("address")
            # the address inside list first element
            addr = f"{address[0]['ip']}/{address[0]['prefix-length']}"
            interface_dict['ipv4'] = addr
        interfaces_list.append(interface_dict)
    return interfaces_list

