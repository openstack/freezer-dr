Openstack Compute High Availability

Osha allows Openstack to have High availability in compute nodes. Simply it monitors all compute nodes in your deployment
and if there is any failure in one of the computes it launches the evacuation tool to evacuate this node and move all
instances to another compute node.

Osha has a plugable architecture so you can use any monitoring system you want to use it for monitoring your compute nodes
just by adding a simple plugin and adjust your configuration file to use this plugin or combination of plugins if you want

Osha runs as scheduler in the control plane which communicates with the monitoring system to get compute nodes status
For running osha under high availability mode, it should run with active passive mode.


