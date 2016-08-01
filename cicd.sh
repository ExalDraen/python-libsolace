#!/bin/bash

/usr/bin/sudo apt-get update
/usr/bin/sudo apt-get -y install python-virtualenv git libxslt1-dev libxml2-dev python-dev libyaml-dev lib32z1-dev
#rm -R -f ~/py27
/usr/bin/virtualenv ~/py27
source ~/py27/bin/activate
/usr/bin/env python setup.py install
pip install --upgrade pip
pip install nose
pip install coverage
chmod 0644 ~/.python-eggs
