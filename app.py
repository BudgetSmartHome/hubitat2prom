import json
import os
import requests
import time

from flask import render_template, Flask

app = Flask(__name__)

base_uri = os.getenv("HE_URI")
access_token = os.getenv("HE_ACCESS_TOKEN")

# This is the default set of metrics to be collected
collected_metrics = [
        "temperature",
        "humidity",
        "battery"
        ]

@app.route("/metrics")
def metrics():
    devices = requests.get(f"{base_uri}?access_token={access_token}")

    device_attributes = []

    for device in devices.json():
        device_details = requests.get(f"{base_uri}/{device['id']}?access_token={access_token}").json()
        for attrib  in device_details['attributes']:
            if attrib["name"] in collected_metrics:
                device_attributes.append({
                    "metric_name": f"{attrib['name']}_{device_details['label'].lower().replace(' ','_').replace('-','_')}",
                    "metric_value": f"{attrib['currentValue']}",
                    "metric_timestamp": time.time()})

    return render_template('base.txt',
            device_details=device_attributes,
            mimetype='text/plain')



