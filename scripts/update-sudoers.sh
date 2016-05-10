echo "Script requires root password to be unlocked!"
su -c "\
    cp -p /etc/sudoers /etc/sudoers.orig && \
    echo -e '${USER}\tALL=NOPASSWD: ALL' >> /etc/sudoers"