About
-----
* This project is aimed at disrupting services in an effort to test High Availability.
* Currently the scope of this effort is limited to the validation of Galera and RabbitMQ.
* The disruptor is only one part of the overall picture. Rally is used to execute traffic against the environment. The idea is to take a container/node offline while continually building nova instances through the use of Rally.

Dir
-----
* ./rally_tasks/nova_create_delete.yaml is the task rally will run. It builds and deletes 200 instances and tracks the success rate.
* disruptor.py is the primary tool used for disrupting the RabbitMQ and Galera clusters.
* LICENSE is the apache license agreement.
* README.rst is this file.
* requirements.txt is a list of all required pip libraries. Installable via pip install -r requiremnts.
* test_disruptor.py are the unit tests for disruptor.py.


Dependencies
-----
* Openstack-Ansible or RPC-O deployment
* tempest installed and run
* Rally needs to be install following these basic instructions, http://rally.readthedocs.io/en/latest/install_and_upgrade/install.html#automated-installation


Usage
-----
1. Start the execution of the Rally task.
    rally task start rally_tasks/nova_create_delete.yaml
2. The execution of disruptor.py can be done anywhere on the "deployment or infra1 node".
    python disruptor.py -s galera --aio
    The disruptory.py takes arguments
        * -w specify the wait time between restarts. 
        * -s *required* this is the service to restart 
        * --aio this is required if you are on an All-In-One deployment 
        * --show Show which services will be restarted, but takes no action
        * --multiple Execute a rolling restart against multiple services simultanously. This will restart one container per service provided at a time.
