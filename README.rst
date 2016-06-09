=========
Yggdrasil
=========

Installation
============
::

$ git clone git@gitlabhost.rtp.raleigh.ibm.com:1A8420897/yggdrasil.git
$ cd yggdrasil
$ ./scripts/update-sudoers.sh
$ ./scripts/install.sh
$ source scripts/setup-env
$ export ANSIBLE_HOST_KEY_CHECKING=False
$ cd playbooks

Configure Network Bridge
========================

Create a network bridge named "br0" with port connected to management
network (192.168.3.0/24).

Below is an example interface defined in the local
"/etc/network/interface" file. Note that "p1p1" is the name of the
interface connected to the management network.

::

    auto br0
    iface br0 inet static
        address 192.168.3.3
        netmask 255.255.255.0
        bridge_ports p1p1

Container Installation
======================
::

$ ansible-playbook -i hosts lxc-create.yml
$ ansible-playbook -i hosts install.yml
