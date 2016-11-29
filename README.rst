========================
Team and repository tags
========================

.. image:: http://governance.openstack.org/badges/freezer-dr.svg
    :target: http://governance.openstack.org/reference/tags/index.html

.. Change things from this point on

=========================
Freezer Disaster Recovery
=========================

freezer-dr, OpenStack Compute node High Available provides compute node high availability for OpenStack.
Simply freezer-dr monitors all compute nodes running in a cloud deployment and if there is any failure
in one of the compute nodes freezer-dr will fence this compute node then freezer-dr will try to evacuate all
running instances on this compute node, finally freezer-dr will notify all users who have workload/instances
running on this compute node as well as will notify the cloud administrators.

freezer-dr has a pluggable architecture so it can be used with:

1. Any monitoring system to monitor the compute nodes (currently we support only native OpenStack services status)
2. Any fencing driver (currently supports IPMI, libvirt, ...)
3. Any evacuation driver (currently supports evacuate api call, may be migrate ??)
4. Any notification system (currently supports email based notifications, ...)

just by adding a simple plugin and adjust the configuration file to use this
plugin or in future a combination of plugins if required

freezer-dr should run in the control plane, however the architecture supports different scenarios.
For running freezer-dr under high availability mode, it should run with active passive mode.


------------
How it works
------------

Starting freezer-dr:

1. freezer-dr Monitoring manager is going to load the required monitoring driver according to the configuration
2. freezer-dr will query the monitoring system to check if it considers any compute nodes to be down ?
3. if no, freezer-dr will exit displaying No failed nodes
4. if yes, freezer-dr will call the fencing manager to fence the failed compute node
5. Fencing manager will load the correct fencer according to the configuration
6. once the compute node is fenced and is powered off now we will start the evacuation process
7. freezer-dr will load the correct evacuation driver
8. freezer-dr will evacuate all instances to another computes
9. Once the evacuation process completed, freezer-dr will call the notification manager
10. The notification manager will load the correct driver based on the configurations
11. freezer-dr will start the notification process ...

