from flask import json
from flask import request
from flask import Flask
from kasa import SmartDimmer
from pprint import pformat as pf
import asyncio

BRIGHTNESS_START_VALUE = 10
BRIGHTNESS_PAUSE_VALUE = 50
BRIGHTNESS_STOP_VALUE = 80

app = Flask(__name__)

@app.route("/")
def api_root(): 
    return "Dimmer Control App"

@app.route("/plex", methods=["POST"])
def api_plex(): 
    data_recieved = json.loads(request.form["payload"])
    
    if (data_recieved["event"] == "media.play" or data_recieved["event"] == "media.resume"):
        asyncio.run(set_to_brightness(BRIGHTNESS_START_VALUE))
    
    elif (data_recieved["event"] == "media.pause"):
        asyncio.run(set_to_brightness(BRIGHTNESS_PAUSE_VALUE))

    elif (data_recieved["event"] == "media.stop"):
        asyncio.run(set_to_brightness(BRIGHTNESS_STOP_VALUE))


    return "Light Toogled"

async def set_to_brightness(brightness): 
    dimmer = SmartDimmer("192.168.78.58")
    await dimmer.update() 

    print (dimmer.state_information)

    if not dimmer.is_on:
        return
    
    await dimmer.set_brightness(brightness)
    
    print (dimmer.state_information)
    
    

if __name__ == "__main__":
    # asyncio.run(set_to_brightness(10))
    app.run(host="0.0.0.0", debug=True)
