# Load Testing

This repository contains the list of resources required for running load tests specifically against an ASR system.

Ensure that the necessary infrastructure has already been set up and installed as followed in [fyp-infra](https://github.com/ernestang98/fyp-infra).

# Project Structure

```bash
└── load-testing
    ├── audio
    ├── constants.js
    └── script.js
```

`script.js` is the load testing suite to be run by `k6`

`constants.js` contains a list of variables used by `script.js`

`audio/` is a directory of audio files used by `script.js`


# Running the load test

To run a load test, simply run the following commands:

```
mkdir reports
K6_INFLUXDB_USERNAME=$K6_INFLUXDB_USERNAME 
K6_INFLUXDB_PASSWORD=$K6_INFLUXDB_PASSWORD 
k6 run -e HOST=$HOST -e PORT=$PORT -e AUDIO_DURATION=$AUDIO_DURATION --out influxdb=$INFLUXDB script.js
```

- K6_INFLUXDB_USERNAME is the username of influxdb if you are streaming metrics to influxdb

- K6_INFLUXDB_PASSWORD is the password of influxdb if you are streaming metrics to influxdb

- HOST is the ip/domain name of your deployed ASR system

- PORT is the port of your deployed ASR system

- AUDIO_DURATION is the duration of the audio to be used in load test, either SHORT, MEDIUM, or LONG

- INFLUXDB is the url of your deployed influxdb instance
