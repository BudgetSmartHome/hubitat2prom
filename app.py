import json
import os
import requests
import time

from flask import render_template, Flask

app = Flask(__name__)

base_uri = os.getenv("HE_URI")
access_token = os.getenv("HE_ACCESS_TOKEN")


@app.route("/metrics")
def metrics():
    devices = requests.get(f"{base_uri}?access_token={access_token}")

    device_attributes = []

    for device in devices.json():
        device_details = requests.get(f"{base_uri}/{device['id']}?access_token={access_token}").json()
        for attrib  in device_details['attributes']:
            if attrib["name"] == "humidity":
                device_attributes.append({
                    "metric_name": f"humidity_{device_details['label'].lower().replace(' ','_')}_humidity",
                    "metric_value": f"{attrib['currentValue']}",
                    "metric_timestamp": time.time()})
            if attrib["name"] == "battery":
                device_attributes.append({
                    "metric_name": f"battery_{device_details['label'].lower().replace(' ','_')}_charge_remaining",
                    "metric_value": f"{attrib['currentValue']}",
                    "metric_timestamp": time.time()})
            if attrib["name"] == "temperature":
                device_attributes.append({
                    "metric_name": f"temperature_{device_details['label'].lower().replace(' ','_')}_current_value",
                    "metric_value": f"{attrib['currentValue']}",
                    "metric_timestamp": time.time()})

    return render_template('base.txt',
            device_details=device_attributes,
            mimetype='text/plain')



