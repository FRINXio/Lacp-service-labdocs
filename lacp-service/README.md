# Aggregate multiple connections with LACP service

In this lab, you will learn about LACP service. It is an example Python application that is using Frinx uniconfig framework to provision simple LACP service. Purpose of the application is to show potentional users of uniconfig how to use it in an efficient and simple manner.

## Objective

* Understand how LACP service can be used to agregate multiple network connections
* Learn how to use LACP service to agregate several parallel connections into 1 logical connection

### Completion Time: XZY minutes

## Prerequisites

* Install and run the FRINX ODL distribution
* Install and run Postman
* Mount 2 routers via Postman environment

For further guidance click on Installation and configuration guide located on top of the page.

## Step 1: Install and configure LACP service application

LACP service application runs on python 3.6 or newer. Go into the application folder directory and execute following command:

```
pip install flask frinx_uniconfig-3.1.7.rc16_frinx_SNAPSHOT-py3-none-any.whl
```

After that change ODL adderss configuration in lacp_service.py. Adjust following lines according to you local setting:

```
configuration.username = 'admin'
configuration.password = 'admin'
configuration.host = 'http://127.0.0.1:8181/restconf'
```

Now you are ready to start the LACP service application

```
export FLASK_APP=lacp_service.py
flask run
```


## Step 2: Provision the LACP service

Now you have application up and running.

Application lacp_service.py exposes really simple and straightforward REST API.  
To provision new LACP service, issue simple POST request:

```
POST http://127.0.0.1:5000/service/new-service
{
    "node1": {
        "name": "xr5",
        "bundle": "122",
        "ports": [
            "GigabitEthernet0/0/0/1",
            "GigabitEthernet0/0/0/3"
        ]
    },
    "node2": {
        "name": "xr6",
        "bundle": "187",
        "ports": [
            "GigabitEthernet0/0/0/2",
            "GigabitEthernet0/0/0/5"
        ]
    }
}
```

The configuration speaks for itself. This bundles GigabitEthernet0/0/0/1 and GigabitEthernet0/0/0/3 interfaces into new bundle with id 122 on node1 and similiarly on other node. 


lacp_service.py internally translates this POST request into openconfig uniconfig based configuration issues several calls to UNICONFIG API and as a result provision the service.


