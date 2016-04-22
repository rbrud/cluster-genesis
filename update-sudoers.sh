su <<'EOF'
cp -p /etc/sudoers /etc/sudoers.orig
sed -i '/^root/a deployer\tALL=NOPASSWD: ALL' /etc/sudoers
EOF
