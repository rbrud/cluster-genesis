=========
Yggdrasil
=========

Installation
===========
::

$ git clone git@gitlabhost.rtp.raleigh.ibm.com:1A8420897/yggdrasil.gitdeployer
$ cd yggdrasil
$ ./scripts/update-sudoers.sh
$ ./scripts/install.sh
$ source scripts/setup-env
$ cd playbooks

Configure IP address
===================

| Change the ``ansible_host`` parameter to that of the deployment host.
|
::

    deployer ansible_user=deployer ansible_port=26 ansible_host=0.0.0.0

Container installation
=====================
::

$ ansible-playbook -i hosts install.yml