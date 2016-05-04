su -c "\
    cp -p /etc/sudoers /etc/sudoers.orig && \
    sed -i '/^root/a ${USER}\tALL=NOPASSWD: ALL' /etc/sudoers"
