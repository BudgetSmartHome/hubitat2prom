# hubitat2prom

This application runs in a docker container, talks to the 
[Hubitat Maker API](https://docs.hubitat.com/index.php?title=Maker_API)
and returns the metrics in a format suitable for consumption by
 [Prometheus](https://prometheus.io)

# Getting up and running

## Docker

This is the recommended way to launch the service as it takes care of the dependencies for you.

First, retrieve your API token and API path from your Hubitat device. These will look something like;

- HE_URI: `http://<hubitat_hostname>/apps/api/26/devices`
- HE_TOKEN: `f4a20ab3-..-670f559be5a6`

Put these values into a new file named `.env` as below:

```
HE_URI=http://<hubitat_hostname>/apps/api/26/devices
HE_TOKEN=f4a20ab3-..-670f559be5a6
```

Next, run the following command to start the container:

```bash
docker run --rm --env-file .env -p 5000:5000 ghcr.io/budgetsmarthome/hubitat2prom:latest
```

You can also use docker-compose if you prefer:

```bash
$ cat <<EOF >docker-compose.yaml
---
version: '3'
services:
  hubitat2prom:
    image: ghcr.io/budgetsmarthome/hubitat2prom:latest
    env_file:
    - '.env'
    ports:
    - 5000:5000

EOF

$ docker-compose run --rm hubitat2prom
```

This will start the container listening on your local machine on port 5000, and you can visit 
[http://localhost:5000/metrics](http://localhost:5000/metrics) to confirm that the metrics are coming through.

You can additionally visit
[http://localhost:5000/info](http://localhost:5000/info) to view basic
configuration infomation and check the connection status with the Hubitat API.

Once you've confirmed this, you can move on to configuring Prometheus.

## Local Installation

If you want to run this service without installing from Docker, then the steps
are as follows:

   1. Install `pipenv` for python3; `python3 -m pip install pipenv`.
   2. Create the `.env` file as per the instructions above.
   3. Run the following command: `pipenv run app`

A Python virtual environment will be created automatically, if the service has
never run before and then pipenv will also automatically install all of the
dependencies that the service requires to run. After this is completed the
application will start. If you stop and start the application, the dependencies
will persist unless otherwise removed.

As with the docker container, your service will now be exposed on port 5000, and
you can test it is working by visiting
[http://localhost:5000/metrics](http://localhost:5000/metrics) in a browser.

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

## InfluxDB

Configuring InfluxDB is equally as simple.

Visit the InfluxDB admin console, then navigate to;
`Data --> Scrapers --> 'Create Scraper'`

Provide a name to your scraper, assign a bucket where the data should be stored,
then provide the path to the metrics path as listed above, substituting your
localhost address with the IP address/hostname of the server running the
container.

![InfluxDB - Create Scraper](/screenshots/influxdb-scraper.jpg)

Metrics data from your new scraper is now available to be queried:

![InfluxDB - Query Metrics](/screenshots/influxdb-query.jpg)

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
