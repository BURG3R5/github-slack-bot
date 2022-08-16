#!/bin/bash

#to install the snapd
sudo apt update
sudo apt install snapd

#to install python
sudo snap install python38

#to install git
sudo snap install git-ubuntu --classic

#Clone this repo
git clone https://github.com/mdg-iitr/github-slack-bot.git
cd github-slack-bot

#create virtual environment
python -m venv venv

#activate the vitual env
source venv/bin/activate

#install the required dependencies for env
pip install -r requirements.txt

#install the hooks
pip install pre-commit
pre-commit install`
