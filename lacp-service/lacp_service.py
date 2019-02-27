from flask import Flask
from flask import request
from swagger_uniconfig import FrinxOpenconfigInterfacesApi, FrinxOpenconfigIfEthernetEthernettopEthernetConfig, \
    FrinxOpenconfigIfEthernetApi, UniconfigManagerApi, Configuration, ApiClient, \
    FrinxOpenconfigInterfacesInterfacestopInterfacesInterfaceConfigRequest, UniconfigManagerTargetnodesfieldsTargetNodes, \
    UniconfigManagerSyncfromnetworkInput, UniconfigManagerSyncfromnetworkInputBodyparam, \
    UniconfigManagerCommitInput, UniconfigManagerCommitInputBodyparam, \
    FrinxOpenconfigInterfacesInterfacestopInterfacesInterfaceConfig, FrinxOpenconfigInterfacesTypeIdentityref, \
    FrinxOpenconfigIfEthernetEthernettopEthernetConfigRequest, FrinxUniconfigTopologyApi

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
    node1_current_interfaces = read_interfaces(node1_name)
    create_bundle(node1_name, bundle_id, node1_current_interfaces)
    add_ports_to_bundle(node1_name, bundle_id, node1_ports, node1_current_interfaces)

    uniconfig_node2 = json_body['node2']
    node2_name = uniconfig_node2['name']
    node2_ports = uniconfig_node2['ports']
    bundle_id = uniconfig_node2['bundle']
    node2_current_interfaces = read_interfaces(node2_name)
    create_bundle(node2_name, bundle_id, node2_current_interfaces)
    add_ports_to_bundle(node2_name, bundle_id, node2_ports, node2_current_interfaces)

    uniconfig_api = UniconfigManagerApi(api_client)

    sync_nodes = UniconfigManagerTargetnodesfieldsTargetNodes([node1_name, node2_name])
    sync_input = UniconfigManagerSyncfromnetworkInput(target_nodes=sync_nodes)
    sync_response = uniconfig_api.rpc_uniconfig_manager_sync_from_network(UniconfigManagerSyncfromnetworkInputBodyparam(sync_input))
    print(sync_response)

    commit_nodes = UniconfigManagerTargetnodesfieldsTargetNodes([node1_name, node2_name])
    commit_input = UniconfigManagerCommitInput(target_nodes=commit_nodes)
    commit_response = uniconfig_api.rpc_uniconfig_manager_commit(UniconfigManagerCommitInputBodyparam(commit_input))
    print(commit_response)
    return str(commit_response)


def read_interfaces(node_name):
    config_response = FrinxUniconfigTopologyApi(
        api_client).get_network_topology_network_topology_topology_node_configuration(
        topology_id='uniconfig',
        node_id=node_name)

    # Example reads

    # print(f"Get entire configuration of a node: {node_name} from uniconfig database")
    # print(config_response.frinx_uniconfig_topologyconfiguration)
    # print(f"Get single interface of a node: {node_name} from uniconfig database")
    # print(config_response.frinx_uniconfig_topologyconfiguration.frinx_openconfig_interfacesinterfaces)
    # print(f"Get single interface name of a node: {node_name} from uniconfig database")
    # print(config_response.frinx_uniconfig_topologyconfiguration.frinx_openconfig_interfacesinterfaces.interface[0]
    #       .config.name)

    # print(f"Get all IPv4 addresses of a node: {node_name} from uniconfig database")
    # for i in config_response.frinx_uniconfig_topologyconfiguration.frinx_openconfig_interfacesinterfaces.interface:
    #    subinterfaces = safe_get(i, "subinterfaces", {'subinterface': []})
    #    subinterface_zero = subinterfaces['subinterface'][0] if subinterfaces['subinterface'] != [] else {}
    #    ipv4 = safe_get(subinterface_zero, "frinx_openconfig_if_ipipv4", {'addresses': {}})
    #    addresses = safe_get(ipv4, "addresses", {'address': []})
    #    print(addresses['address'])

    ifc_names = []
    for i in config_response.frinx_uniconfig_topologyconfiguration.frinx_openconfig_interfacesinterfaces.interface:
        ifc_names.append(i.config.name)

    return ifc_names


def safe_get(data, attribute, default):
    data_default = data if data else {}
    data_dict = data if isinstance(data_default, dict) else data.to_dict()
    value = data_dict[attribute] if attribute in data_dict and data_dict[attribute] else default
    return value if isinstance(value, dict) else value.to_dict()


def add_port_to_bundle(node_id, bundle_id, port):
    bundle_ifc_name = 'Bundle-Ether' + bundle_id
    port_ifc_eth_config = FrinxOpenconfigIfEthernetEthernettopEthernetConfig(
        frinx_openconfig_if_aggregateaggregate_id=bundle_ifc_name
    )
    port_ifc_eth = FrinxOpenconfigIfEthernetEthernettopEthernetConfigRequest(
        frinx_openconfig_if_ethernetconfig=port_ifc_eth_config
    )
    etc_ifc_api = FrinxOpenconfigIfEthernetApi(api_client)
    etc_ifc_api.put_network_topology_network_topology_topology_node_configuration_interfaces_interface_ethernet_config(
        topology_id='uniconfig', node_id=node_id, name=port,
        frinx_openconfig_if_ethernet_ethernettop_ethernet_config_body_param=port_ifc_eth
    )


def add_ports_to_bundle(node_id, bundle_id, ports, node1_current_interfaces):
    for port in ports:
        if port not in node1_current_interfaces:
            raise Exception(f'Interface {port} does not exist on {node_id}')
        else:
            add_port_to_bundle(node_id, bundle_id, port)


def create_bundle(node_id, bundle_id, node_current_interfaces):
    bundle_ifc_name = 'Bundle-Ether' + bundle_id

    if bundle_ifc_name in node_current_interfaces:
        raise Exception(f'Interface {bundle_ifc_name} already exists on {node_id}')

    bundle_ifc_config = FrinxOpenconfigInterfacesInterfacestopInterfacesInterfaceConfig(
        type=FrinxOpenconfigInterfacesTypeIdentityref.IANA_IF_TYPE_IEEE8023ADLAG,
        enabled=True, name=bundle_ifc_name
    )
    bundle_ifc = FrinxOpenconfigInterfacesInterfacestopInterfacesInterfaceConfigRequest(
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
        #return configure_service(service_id, request.get_json())
        return configure_service(service_id, request.get_json())



