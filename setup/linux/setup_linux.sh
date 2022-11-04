#!/bin/bash

#to install the snapd
# if ! hash snap &> /dev/null ; then
#     sudo apt update
#     echo "===============Downloading snap========================================================================="
#     sudo apt install snapd
# fi

#to install python
# if ! hash python38 &> /dev/null ; then
#     sudo snap install python38
#     echo "========================================================================================================="
# fi


#to install git

# if ! hash git &> /dev/null ; then
#     sudo snap install git-ubuntu --classic
#     echo "========================================================================================================="
# fi

#Clone this repo
# git clone https://github.com/mdg-iitr/github-slack-bot.git
# cd github-slack-bot

#create virtual environment
python3 -m venv venv

#activate the vitual env
source venv/bin/activate

#install the required dependencies for env
pip install -r requirements.txt

#install the hooks
if ! hash pre-commit &> /dev/null ; then
    pip install pre-commit
    pre-commit install
    echo "========================================================================================================="
fi
