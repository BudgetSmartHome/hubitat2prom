# hubitat2prom

This application runs in a docker container, talks to the 
[Hubitat Maker API](https://docs.hubitat.com/index.php?title=Maker_API)
and returns the metrics in a format suitable for consumption by
 [Prometheus](https://prometheus.io)

# Getting up and running

## Docker

This is the recommended way to launch the service as it takes care of the dependencies for you.

First, update the `config/hubitat2prom.yml` file with the URL and access token for your MakerAPI.  This can be found
in the MakerAPI settings on your Hubitat device.

Next, run the following command to start the container:

`docker run -v "$(pwd)"/config:/app/config -p 5000:5000 proffalken/hubitat2prom:latest`

This will start the container listening on your local machine on port 5000, and you can visit 
[http://localhost:5000/metrics](http://localhost:5000/metrics) to confirm that the metrics are coming through.

Once you've confirmed this, you can move on to configuring Prometheus.

## Local Installation

If you want to run this service without installing from Docker, then the steps are as follows:

   1. Configure `config/hubitat2prom.yml` as documented in the `Docker` section of this readme.
   2. Install the requirements from `requirements.txt` into an appropriate virtual environment
   3. Run the following command: `export FLASK_APP=app;export HEPROM_CFG_FILE="path/to/config/file" && flask run`

As with the docker container, your service will now be exposed on port 5000, and you can test it is working
by visiting [http://localhost:5000/metrics](http://localhost:5000/metrics) in a browser.

## Prometheus

Configuring Prometheus to scrape the metrics is easy.

Add the following to the bottom of your Prometheus Outputs:

```
  - job_name: 'hubitat'
    scrape_interval: 30s
    static_configs:
    - targets: ['my.ip.address.or.hostname']
```

Prometheus will now scrape your web service every 30 seconds to update the metrics in the data store.

# Collected Metrics

Hubitat2Prom is capable of collecting any of the metrics that Hubitat exposes via the MakerAPI.

By default it will collect the list below, however adding a new metric is as simple as checking the output of the MakerAPI and adding the attribute name to your configuration, and then restarting the service.

The default collections are:

```
  - battery
  - humidity
  - illuminance
  - level # This is used for both Volume AND Lighting Dimmers!
  - switch # We convert from "on/off" to "1/0" so it can be graphed
  - temperature
```

# Grafana

There's a sample dashboard in the [grafana/](grafana) directory that you can [import into Grafana](https://grafana.com/docs/grafana/latest/dashboards/export-import/#importing-a-dashboard) to give you an idea of what is possible!

![The sample Grafana dashboard](/screenshots/Hubitat2promOverview.png)
