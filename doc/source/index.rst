=====================================================
Welcome to Freezer's Disaster Recovery documentation!
=====================================================

freezer-dr, OpenStack Compute node High Available provides compute node high
availability for OpenStack. Simply freezer-dr monitors all compute nodes running
in a cloud deployment and if there is any failure in one of the compute nodes
freezer-dr will fence this compute node then freezer-dr will try to evacuate
all running instances on this compute node, finally freezer-dr will notify all
users who have workload/instances running on this compute node as well as will
notify the cloud administrators.


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. toctree::
   :maxdepth: 1

   api/modules
