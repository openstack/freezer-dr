==================
OSHA
==================

Osha, Openstack Compute node High Available provides compute node high availability for OpenStack.
Simply Osha monitors all compute nodes running in a cloud deployment and if there is any failure
in one of the compute nodes osha will fence this compute node then osha will try to evacuate all
running instances on this compute node, finally Osha will notify all users who have workload/instances
running on this compute node as well as will notify the cloud administrators.

Osha has a pluggable architecture so it can be used with:

1. Any monitoring system to monitor the compute nodes (currently we support only native openstack services status)
2. Any fencing driver (currently supports IPMI, libvirt, ...)
3. Any evacuation driver (currently supports evacuate api call, may be migrate ??)
4. Any notification system (currently supports email based notifications, ...)

just by adding a simple plugin and adjust the configuration file to use this
plugin or in future a combination of plugins if required

Osha should run in the control plane, however the architecture supports different scenarios.
For running osha under high availability mode, it should run with active passive mode.


-----------------
How it works
-----------------

Starting Osha
1. Osha Monitoring manager is going to load the required monitoring driver according to the configuration
2. Osha will query the monitoring system to check if it considers any compute nodes to be down ?
3.1. if no, Osha will exit displaying No failed nodes
3.2. if yes, Osha will call the fencing manager to fence the failed compute node
4. Fencing manager will load the correct fencer according to the configuration
5. once the compute node is fenced and is powered off now we will start the evacuation process
6. Osha will load the correct evacuation driver
7. Osha will evacuate all instances to another computes
8. Once the evacuation process completed, Osha will call the notification manager
9. The notification manager will load the correct driver based on the configurations
10. Osha will start the notification process ...
