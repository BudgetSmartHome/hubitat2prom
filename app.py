import json
import os
import requests
import time
import yaml

from flask import render_template, Flask, make_response

app = Flask(__name__)

# Load the config file
config_file = os.getenv("HE2PROM_CFG_FILE") or "/app/config/hubitat2prom.yml"
with open(config_file, "r") as configfile:
    config = yaml.load(
            configfile,
            Loader=yaml.SafeLoader)

base_uri = config["hubitat"]["base_uri"]
access_token = config["hubitat"]["access_token"]

# This is the default set of metrics to be collected
collected_metrics = config['collected_metrics']

@app.route("/metrics")
def metrics():
    devices = requests.get(f"{base_uri}?access_token={access_token}")

    device_attributes = []

    for device in devices.json():
        device_details = requests.get(f"{base_uri}/{device['id']}?access_token={access_token}").json()
        for attrib  in device_details['attributes']:
            # Is this a metric we should be collecting?
            if attrib["name"] in collected_metrics:
                # Does it have a "proper" value?
                if attrib["currentValue"] is not None:
                    # If it's a switch, then change from text to binary values
                    if attrib["name"] == "switch":
                        if attrib["currentValue"] == "on":
                            attrib["currentValue"] = 1
                        else:
                            attrib["currentValue"] = 0
                    # Sanitise the device name as it will appear in the label
                    device_name = device_details['label'].lower().replace(' ','_').replace('-','_')
                    metric_name = attrib['name'].lower().replace(' ','_').replace('-','_')
                    # Create the dict that holds the data
                    device_attributes.append({
                        "device_name": f"{device_name}",
                        "metric_name": f"{metric_name}",
                        "metric_value": f"{attrib['currentValue']}",
                        "metric_timestamp": time.time()})
    # Create the response
    response = make_response(render_template('base.txt',
            device_details=device_attributes
            ))
    # Make sure we return plain text otherwise Prometheus complains
    response.mimetype = "text/plain"
    return response



