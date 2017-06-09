#!/usr/bin/env python
# Copyright 2017, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# (c) 2017, Nolan Brubaker <nolan.brubaker@rackspace.com>
# (c) 2017, Ryan Dorothy <ryan.dorothy@rackspace.com>

import argparse
import json
import logging
import os
import subprocess
import sys
import time

logger = logging.getLogger(__name__)


CONF_DIR = os.path.join('/', 'etc', 'openstack_deploy')
INVENTORY_FILE = os.path.join(CONF_DIR, 'openstack_inventory.json')
CONF_FILE = os.path.join(CONF_DIR, 'openstack_user_config.yml')
PLAYBOOK_DIR = os.path.join('/', 'opt', 'openstack_ansible', 'playbooks')

STOP_TEMPLATE = 'ansible -i inventory -m shell -a\
        "lxc-stop -n {container}" {host}'
START_TEMPLATE = 'ansible -i inventory -m shell -a\
        "lxc-start -dn {container}" {host}'

supported_services = ['rabbitmq', 'galera']
DEFAULT_WAIT = 120


def configure_logging():
    logger.setLevel(logging.INFO)
    console = logging.StreamHandler()
    logfile = logging.FileHandler('/var/log/rolling_restart.log', 'a')

    console.setLevel(logging.INFO)
    logfile.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # Make sure we're using UTC for everything.
    formatter.converter = time.gmtime

    console.setFormatter(formatter)
    logfile.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(logfile)


def args(arg_list):
    parser = argparse.ArgumentParser(
        usage='%(prog)s',
        description='OpenStack-Ansible Rolling Update Simulator',
        epilog='Licensed "Apache 2.0"')

    parser.add_argument(
        '--aio',
        help='This indicates your deployment is an All In One',
        action='store_true'
    )

    parser.add_argument(
        '-m',
        '--multiple',
        help='Execute a rolling restart against multiple services '
             'simultaneously. This will only restart one container per service'
             ' at a time.',
        action='store_true'
    )

    parser.add_argument(
        '-s',
        '--service',
        help='Name of the service to rolling restart. Valid services that can'
             ' be passed in are {0}'.format(", ".join(supported_services)),
        metavar='N',
        nargs='+',
        required=True,
        default=None,
        choices=supported_services
    )

    parser.add_argument(
        '--show',
        help='Show which services will be restarted, but takes no action',
        action='store_true'

    )

    parser.add_argument(
        '-w',
        '--wait',
        help=("Number of seconds to wait between stopping and starting. "
              "Default: {0}".format(DEFAULT_WAIT)),
        default=DEFAULT_WAIT,
    )

    return vars(parser.parse_args(arg_list))


def read_inventory(inventory_file):
    """Parse inventory file into a python dictionary
    :param inventory_file -- indicates the location of inventory file
    """
    with open(inventory_file, 'r') as f:
        inventory = json.load(f)
    return inventory


def get_similar_groups(target_group, inventory):
    """
    Find group suggestions
    :param target_group: Service to be disrupted
    :param inventory: Parsed inventory file
    """
    suggestions = []
    for key in inventory.keys():
        if target_group in key:
            suggestions.append(key)
    return suggestions


def get_containers_by_group(target_group, inventory):
    """Get container names in the relevant group
    :param target_group: Service to be disrupted
    :param inventory: Parsed inventory file
    """

    group = inventory.get(target_group, None)

    if group is None:
        groups = get_similar_groups(target_group, inventory)
        print("No group {} found.".format(target_group))
        if groups:
            print("Maybe try one of these:")
            print("\n".join(groups))
        sys.exit(1)

    containers = group['hosts']
    containers.sort()
    return containers


def get_containers(services, inventory, multiple):
    containers = []
    for i in services:
        if multiple:
            containers.append(get_containers_by_group(i, inventory))
        else:
            containers += get_containers_by_group(i, inventory)
    return containers


def rolling_restart(containers, inventory, aio, wait=120):
    """Restart containers in numerical order, one at a time.
    :param wait: is the number of seconds to wait between stopping and
    starting a container
    :param containers: The specific containers to disrupt based on service
    :param inventory: Parsed inventory file
    :param aio: This is a flag to determine if the deployment is an aio
    which determines if the host is localhost or looks for it in inventory
    """
    # Grab a handle to /dev/null so we don't pollute console output with
    # Ansible stuff
    FNULL = open(os.devnull, 'w')
    for container in containers:
        if aio:
            host = 'localhost'
        else:
            host = inventory['_meta']['hostvars'][container]['physical_host']
        stop_cmd = STOP_TEMPLATE.format(container=container, host=host)
        logger.info("Stopping {container}".format(container=container))
        subprocess.check_call(stop_cmd, shell=True, stdout=FNULL,
                              stderr=subprocess.STDOUT)

        time.sleep(wait)

        start_cmd = START_TEMPLATE.format(container=container, host=host)
        subprocess.check_call(start_cmd, shell=True, stdout=FNULL,
                              stderr=subprocess.STDOUT)
        logger.info("Started {container}".format(container=container))

        # To allow Galera cluster to come back online before the next
        # container is taken offline.
        time.sleep(wait / 2)


def show_services_only(aio, containers, multiple, wait):
    """Output the services that will be restarted once --show is not passed.
    Also output if the deployment lab is an All In One and what the wait
    time is.
    :param wait: is the number of seconds to wait between stopping and
    starting a container
    :param containers: The specific containers to disrupt based on service
    :param aio: This is a flag to determine if the deployment is an aio
    which determines if the host is localhost or looks for it in inventory
    :return: Output what would be executed but does not execute the
    rolling_restart.
    """
    if aio:
        logger.info("Your deployment is an All In One")
    if multiple:
        print 'add the logic here'
    else:
        container_list = map(lambda x: x.encode('utf-8'), containers)
        container_str = ', '.join(container_list)
        logger.info("We will be stopping {container} for {wait} and then "
                    "restarting them.".format(container=container_str,
                                              wait=wait))


def main():
    all_args = args(sys.argv[1:])
    service = all_args['service']
    wait = all_args['wait']
    aio = all_args['aio']
    show = all_args['show']
    multiple = all_args['multiple']

    configure_logging()
    inventory = read_inventory(INVENTORY_FILE)
    containers = get_containers(service, inventory, multiple)

    if show:
        show_services_only(aio, containers, multiple, wait)
    elif multiple:
        print "Add logic here"
    else:
        rolling_restart(containers, inventory, aio, wait)

if __name__ == "__main__":
    main()
