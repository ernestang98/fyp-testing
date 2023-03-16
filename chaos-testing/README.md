# Chaos Testing

This repository contains the list of resources required for running chaos experiments specifically against an ASR system.

Ensure that the necessary infrastructure has already been set up and installed as followed in [fyp-infra](https://github.com/ernestang98/fyp-infra).

# Project Structure

```bash
└── chaos-testing
    ├── chaos-experiment-manifests
    │   ├── chaos-cpu-stress-manifests
    │   ├── chaos-mem-stress-manifests
    │   └── chaos-pod-failure-manifests
    └── chaos-verification.py
```

# Running the Chaos Experiments

For my final year project, we have prepared three different types of experiment that will be applied to either the worker, the master, or both worker and master pods:

1. Pod Failure (cause target pod to fail)

2. CPU Stress (cause target pod to require more CPU)

3. Memory Stress (cause target pod to require more memory)

In order to apply chaos into the target pods, simply create it using kubectl:

```
kubectl apply -f MANIFESTS.yaml
```

# Verification during Chaos Experiments

In this directory is also `chaos-verification.py` which is a python script that can enable you to verify the availability of worker and master and hence observe if the deployment is able to handle applied chaos

```
python3 chaos-verification.py --target 1/2/3 --duration 0.5
```

- Set WS_INGRESS and HTTP_INGRESS variables before running

- `--target` defines what are we observing, where 1 represents the master pod, 2 represents the worker pod and 3 represents both worker and master pods

- `--duration` is the duration to observe target for in minutes