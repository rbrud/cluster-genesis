FROM ubuntu:14.04
RUN apt-get update && \
    apt-get -y upgrade
RUN groupadd -r deployer && useradd -r -g deployer deployer
RUN cp -p /etc/sudoers /etc/sudoers.orig
RUN sed -i '/^root/a deployer\tALL=NOPASSWD: ALL' /etc/sudoers
