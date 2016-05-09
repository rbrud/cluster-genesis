sudo apt-get -y install python-pip python-dev
if [[ $(lsb_release -sr) == "14.04" ]]; then
    sudo apt-get -y install libffi-dev libssl-dev
fi
sudo -H pip install --upgrade pip
sudo -H pip install --upgrade setuptools
sudo -H pip install --upgrade wheel
sudo -H pip install virtualenv
virtualenv --no-wheel --system-site-packages deployenv
source deployenv/bin/activate
pip install --ignore-installed ansible
deactivate
