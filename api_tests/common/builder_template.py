from jinja2 import Environment, PackageLoader
import logging

logger = logging.getLogger(__name__)


class TemplateBuilder:
    """ Template builder class to generate yaml or xml file from templates
    The templates are jinja files under /template directory contain template format with naming params for creating
    different types of files.
    Example:
    <interface type="network">
    <mac address="{{mac_address}}"/>
    <source network="{{network_name}}"/>
    <model type="virtio"/>
     <address type="pci" domain="0x0000"/>
    </interface>

    The template directory takes generic builder and update the params in the jinja file.
    For each file template we create a class builder handle the creation.
    The creation flow:

    class RacInterface:  ---> the product defines all jinja related params (using same param name from file)
    def __init__(self):
        self.mac_address = None
        self.network_name = None


    class RacInterfaceBuilder(TemplateBuilder): ---> The builder to set the params values / split by methods
        def attach_interface(self, mac_address, network_name):
            self.network_template.mac_address = mac_address
            self.network_template.network_name = network_name

    Create the director accepts builder and return formated string

    """
    def __init__(self, template):
        self.template = template

    def get_params(self):
        return self.template.__dict__


class TemplateDirector:
    def __init__(self, template_builder: TemplateBuilder):
        self.template_builder = template_builder

    def j2_params(self) -> dict:
        return self.template_builder.get_params()


def generate_builder(template_name, package_path,  **kwargs) -> str:
    env = Environment(loader=PackageLoader("api_tests", package_path=package_path))
    template = env.get_template(template_name)
    template_format = template.render(**kwargs)
    logger.debug(f"Creating the '{template_format}'")
    return template_format

