import logging
import openshift_client as oc
import subprocess

logger = logging.getLogger(__name__)
oc_client = oc


def oc_select(resource, namespace):
    with oc.project(namespace):
        try:
            logger.debug(f"oc_select {resource}' on project '{namespace}'")
            output = oc.selector(resource).objects()
            return output
        except oc.OpenShiftPythonException as e:
            raise RuntimeError(f"Unable to get object {resource} -> {str(e)}")
    return None


def oc_create(str_dict, cmd_args=None, namespace=None):
    # namespace should be detected from yaml.
    with oc.project(namespace):
        try:
            logger.debug(f"oc_create '{str_dict}' on project '{namespace}'")
            output = oc.create(str_dict, cmd_args)
            return output
        except oc.OpenShiftPythonException as e:
            raise RuntimeError(f"Unable to create object {str_dict}: {str(e)}")
    return None


def oc_node_interfaces_ip():
    """list of interface with ipv4
    example: [{"name": "eth1", "ipv4": "10.1.1.1/24"},}]
    """
    interfaces = oc_select("nns", "default")[0].as_dict()['status']['currentState']['interfaces']
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


def run_shell_command(cmd):
    cmd = cmd.split()
    logger.debug(f"oc_run_shell_command {cmd}")
    try:
        subprocess.run(cmd)
    except subprocess.CalledProcessError as e:
        logger.error(e)

