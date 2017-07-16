# Lights-Back-End
This repo is to be used on a raspberry pi to control addressable LED lights. This repo contains the code that allows the raspberry pi to connect to a CloudMQTT broker and subscribe/publish to certain topics. If you clone this repo, make sure to change the domain, port, username and password for your client.connect() function, otherwise it will not work (you will connect to my broker instead of yours). You can get a free broker through [CloudMQTT](www.cloudmqtt.com). Or, you can spin up your own one using Mosquito. 

## Installation
1. Edit backend.py to use your own domain, port, username and password to connect to your MQTT broker. *DO NOT USE MINE*
2. (Optional) set up a python3 virtual environment using `python3 -m venv venv`. This will create a new folder called venv that has everything you need for a virtual environment. To activate, `$ . venv/bin/activate`. To deactivate, `$ deactivate`.
3. Install python dependencies `pip install -r requirements.txt`
4. Run the program `$ python backend.py`
5. Enjoy.
