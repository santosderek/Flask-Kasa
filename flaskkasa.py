from flask import json
from flask import request
from flask import Flask
from kasa import SmartDimmer
from os import mkdir
from pprint import pformat as pf
import asyncio
import os.path

BRIGHTNESS_START_VALUE = 10
BRIGHTNESS_PAUSE_VALUE = 50
BRIGHTNESS_STOP_VALUE = 80

CONFIG_LOCATION = "/home/derek/.config/flask-kasa/"
CONFIG_FILE = "kasa.json"

def get_kasa_config():
    
    data = {}

    if not os.path.exists(CONFIG_LOCATION): 
        app.logger.info ("{} does not exist! Creating...".format(CONFIG_LOCATION))
        mkdir(CONFIG_LOCATION)

    if os.path.exists(os.path.join(CONFIG_LOCATION, CONFIG_FILE)): 
        app.logger.info("{} found!".format(os.path.join(CONFIG_LOCATION, CONFIG_FILE)))

        with open(os.path.join(CONFIG_LOCATION, CONFIG_FILE), 'r') as current_file:
            data = json.loads(current_file.read())

    else:
        app.logger.info ("{} does not exist! Creating...".format(os.path.join(CONFIG_LOCATION, CONFIG_FILE)))
        data = json.loads('{"host":"", "user":"", "BRIGHTNESS_START_VALUE":10, "BRIGHTNESS_PAUSE_VALUE":50, "BRIGHTNESS_STOP_VALUE":80}')
        with open(os.path.join(CONFIG_LOCATION, CONFIG_FILE), 'w') as current_file:
            current_file.write(json.dumps(data, indent=4))
        app.logger.info("Please configue {}!".format(os.path.join(CONFIG_LOCATION, CONFIG_FILE)))
        

    return data


app = Flask(__name__)

@app.route("/")
def api_root(): 
    return "Dimmer Control App"

@app.route("/plex", methods=["POST"])
def api_plex(): 
    default_message = "Light Toogling Through Plex" 

    data_recieved = json.loads(request.form["payload"]) 
    config = get_kasa_config()

    if config["user"] and not config["user"] == data_recieved["Account"]["title"]: 
        return default_message
    
    app.logger.info("User {} found!".format(config["user"]))

    if (data_recieved["event"] == "media.play" or data_recieved["event"] == "media.resume"):
        asyncio.run(set_to_brightness(config["BRIGHTNESS_START_VALUE"]))
    
    elif (data_recieved["event"] == "media.pause"):
        asyncio.run(set_to_brightness(config["BRIGHTNESS_PAUSE_VALUE"]))

    elif (data_recieved["event"] == "media.stop"):
        asyncio.run(set_to_brightness(config["BRIGHTNESS_STOP_VALUE"]))

    return default_message

async def set_to_brightness(brightness): 
    config = get_kasa_config()
    
    dimmer = SmartDimmer(config["host"])
    await dimmer.update() 

    app.logger.info("Brightness is at {}%".format(dimmer.state_information["Brightness"]))
    app.logger.info("Setting brightness to {}%".format(dimmer.state_information["Brightness"]))

    if not dimmer.is_on:
        return
    
    await dimmer.set_brightness(brightness)
    
    
    

if __name__ == "__main__":
    

    if not os.path.exists(CONFIG_LOCATION): 
        print ("{} does not exist! Creating...".format(CONFIG_LOCATION))
        mkdir(CONFIG_LOCATION)

    if not os.path.exists(os.path.join(CONFIG_LOCATION, CONFIG_FILE)):
        print ("{} does not exist! Creating...".format(CONFIG_FILE))
        data = json.loads('{"host":"", "user":"", "BRIGHTNESS_START_VALUE":10, "BRIGHTNESS_PAUSE_VALUE":50, "BRIGHTNESS_STOP_VALUE":80}')

        with open(os.path.join(CONFIG_LOCATION, CONFIG_FILE), 'w') as current_file:
            current_file.write(json.dumps(data, indent=4))
        print ("Please configue {}!".format(os.path.join(CONFIG_LOCATION, CONFIG_FILE)))
        exit()


    app.run(host="0.0.0.0", debug=True)
