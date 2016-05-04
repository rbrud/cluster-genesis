=========
Yggdrasil
=========

Installation
===========

::

$ git clone git@gitlabhost.rtp.raleigh.ibm.com:1A8420897/yggdrasil.git
$ cd yggdrasil
$ ./scripts/update-sudoers.sh
$ ./scripts/install.sh
$ source scripts/setup-env
$ cd playbooks
$ ansible-playbook -i hosts install.yml