echo "Script requires root password to be unlocked!"
su -c "\
    cp -p /etc/sudoers /etc/sudoers.orig && \
    echo '${USER}    ALL=NOPASSWD: ALL' >> /etc/sudoers"

