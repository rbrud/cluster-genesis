dpkg -l python-pip &> /dev/null
if (($?))
then
    sudo apt-get -y install python-pip
fi
sudo -H pip install --upgrade pip
sudo -H pip install --upgrade setuptools
sudo -H pip install --upgrade wheel
sudo -H pip install virtualenv
virtualenv --no-wheel --system-site-packages deployenv
source deployenv/bin/activate
pip install --ignore-installed ansible
deactivate
