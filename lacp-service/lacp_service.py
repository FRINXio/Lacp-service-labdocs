from flask import Flask
from flask import request
from swagger_uniconfig import FrinxOpenconfigInterfacesApi, FrinxOpenconfigIfEthernetEthernettopEthernetConfig, \
    FrinxOpenconfigIfEthernetApi, UniconfigManagerApi, Configuration, ApiClient, \
    FrinxOpenconfigInterfacesInterfacestopInterfacesInterface, UniconfigManagerCalculatediffInputTargetnodes, \
    UniconfigManagerCommitInput, UniconfigManagerCommitInputBodyparam, \
    FrinxOpenconfigInterfacesInterfacestopInterfacesInterfaceConfig, FrinxOpenconfigInterfacesTypeIdentityref, \
    FrinxOpenconfigIfEthernetEthernettopEthernet

app = Flask(__name__)

configuration = Configuration()
configuration.username = 'admin'
configuration.password = 'admin'
configuration.host = 'http://127.0.0.1:8181/restconf'

api_client = ApiClient(configuration)


def configure_service(service_id, json_body):
    app.logger.info('%s configuring service', json_body)
    uniconfig_node1 = json_body['node1']
    node1_name = uniconfig_node1['name']
    node1_ports = uniconfig_node1['ports']
    bundle_id = uniconfig_node1['bundle']
    create_bundle(node1_name, bundle_id)
    add_ports_to_bundle(node1_name, bundle_id, node1_ports)

    uniconfig_node2 = json_body['node2']
    node2_name = uniconfig_node2['name']
    node2_ports = uniconfig_node2['ports']
    bundle_id = uniconfig_node2['bundle']
    create_bundle(node2_name, bundle_id)
    add_ports_to_bundle(node2_name, bundle_id, node2_ports)

    uniconfig_api = UniconfigManagerApi(api_client)
    commit_nodes = UniconfigManagerCalculatediffInputTargetnodes([node1_name, node2_name])
    commit_input = UniconfigManagerCommitInput(target_nodes=commit_nodes)
    uniconfig_api.rpc_uniconfig_manager_commit(UniconfigManagerCommitInputBodyparam(commit_input))


def add_port_to_bundle(node_id, bundle_id, port):
    bundle_ifc_name = 'Bundle-Ether' + bundle_id
    port_ifc_eth_config = FrinxOpenconfigIfEthernetEthernettopEthernetConfig(
        frinx_openconfig_if_aggregateaggregate_id=bundle_ifc_name
    )
    port_ifc_eth = FrinxOpenconfigIfEthernetEthernettopEthernet(
        frinx_openconfig_if_ethernetconfig=port_ifc_eth_config
    )
    etc_ifc_api = FrinxOpenconfigIfEthernetApi(api_client)
    etc_ifc_api.put_network_topology_network_topology_topology_node_configuration_interfaces_interface_ethernet_config(
        topology_id='uniconfig', node_id=node_id, name=port,
        frinx_openconfig_if_ethernet_ethernettop_ethernet_config_body_param=port_ifc_eth
    )


def add_ports_to_bundle(node_id, bundle_id, ports):
    for port in ports:
        add_port_to_bundle(node_id, bundle_id, port)


def create_bundle(node_id, bundle_id):
    bundle_ifc_name = 'Bundle-Ether' + bundle_id
    bundle_ifc_config = FrinxOpenconfigInterfacesInterfacestopInterfacesInterfaceConfig(
        frinx_openconfig_interfacestype=FrinxOpenconfigInterfacesTypeIdentityref.IANA_IF_TYPE_IEEE8023ADLAG,
        frinx_openconfig_interfacesenabled=True, frinx_openconfig_interfacesname=bundle_ifc_name
    )
    bundle_ifc = FrinxOpenconfigInterfacesInterfacestopInterfacesInterface(
        frinx_openconfig_interfacesconfig=bundle_ifc_config
    )
    ifc_api = FrinxOpenconfigInterfacesApi(api_client)
    ifc_api.put_network_topology_network_topology_topology_node_configuration_interfaces_interface_config(
        topology_id='uniconfig', node_id=node_id, name=bundle_ifc_name,
        frinx_openconfig_interfaces_interfacestop_interfaces_interface_config_body_param=bundle_ifc
    )
    

@app.route('/service/<service_id>', methods=['POST'])
def service(service_id):
    if request.method == 'POST':
        return configure_service(service_id, request.get_json())


