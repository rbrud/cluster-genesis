DISTRIB_RELEASE=$(lsb_release -sr)
sudo apt-get -y install python-pip python-dev libffi-dev libssl-dev
if [[ $DISTRIB_RELEASE == "14.04" ]]; then
    sudo apt-get -y install lxc-dev
fi
sudo -H pip install --upgrade pip
sudo -H pip install --upgrade setuptools
sudo -H pip install --upgrade wheel
if [[ $DISTRIB_RELEASE == "14.04" ]]; then
    sudo -H pip install lxc-python2 
fi
sudo -H pip install virtualenv
virtualenv --no-wheel --system-site-packages deployenv
source deployenv/bin/activate
pip install --ignore-installed ansible
deactivate
