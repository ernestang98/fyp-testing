# fyp-testing

This repository contains the list of resources required for running the three types of testing proposed to ensure security and reliability of deployments in Kubernetes:

1. Chaos Testing

2. Load Testing

3. Security Testing

Ensure that the necessary infrastructure has already been set up and installed as followed in [fyp-infra](https://github.com/ernestang98/fyp-infra).

# Project Structure

```bash
├── chaos-testing
│   ├── chaos-experiment-manifests
│   └── chaos-verification.py
├── load-testing
│   ├── audio
│   ├── constants.js
│   └── script.js
└── security-testing
    ├── semgreo-manifests
    ├── defect-dojo-send-report.py
    └── sca-owasp-dependency-check.sh
```