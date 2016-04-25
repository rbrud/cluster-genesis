FROM ubuntu:14.04
RUN groupadd -r deployer && useradd -m -r -g deployer deployer
RUN cp -p /etc/sudoers /etc/sudoers.orig
RUN sed -i '/^root/a deployer\tALL=NOPASSWD: ALL' /etc/sudoers
RUN sudo apt-get update && sudo apt-get -y upgrade
RUN sudo apt-get -y install python-pip python-dev
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --upgrade wheel
RUN pip install virtualenv
USER deployer
RUN mkdir -p /home/deployer/ygg
RUN virtualenv --no-wheel --system-site-packages /home/deployer/ygg/deployenv
RUN /bin/bash -c "source /home/deployer/ygg/deployenv/bin/activate \
    && pip install --ignore-installed ansible \
    && deactivate"
