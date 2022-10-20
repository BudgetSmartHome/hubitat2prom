import json
import os
import requests
import time

from flask import render_template, Flask, make_response, Response

app = Flask(__name__)

# Load the configuration values from environment variables - HE_URI and HE_TOKEN
# are mandatory, however a default collection of metrics is provided if the
# HE_METRICS env is missing.
try:
    base_uri = os.environ["HE_URI"]
    access_token = os.environ["HE_TOKEN"]
    collected_metrics = os.getenv("HE_METRICS", "battery,humidity,illuminance,level,switch,temperature,power,energy").split(",")
except KeyError as e:
    print(f"Could not read the environment variable - {e}")

def get_devices():
    return requests.get(f"{base_uri}?access_token={access_token}")

@app.route("/info")
def info():
    res = {
        "status": {
            "CONNECTION": "ONLINE" if get_devices().status_code == 200 else "OFFLINE"
        },
        "config": {
            "HE_URI": base_uri,
            "HE_TOKEN": access_token,
            "HE_METRICS": collected_metrics
        }
    }
    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/metrics")
def metrics():
    devices = get_devices()
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
                    if attrib["name"] == "water":
                        if attrib["currentValue"] == "dry":
                            attrib["currentValue"] = 1
                        else:
                            attrib["currentValue"] = 0
                    if attrib["name"] == "power":
                        if attrib["currentValue"] == "on":
                            attrib["currentValue"] = 1
                        elif attrib["currentValue"] == "off":
                            attrib["currentValue"] = 0
                        else:
                            attrib["currentValue"] = attrib["currentValue"]

                    # Sanitise the device name as it will appear in the label
                    device_name = device_details['label'].lower().replace(' ','_').replace('-','_')
                    # Sanitise the metric name 
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



