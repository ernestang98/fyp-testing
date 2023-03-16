# Security Testing

This repository contains the list of resources required for running security tests specifically against an ASR system. Note that majority of the tests are done via using open sourced software (e.g. Checkov, SonarQube) and do not require additional resources. Therefore, the resources present here are meant to support the few tests that requires them in our automated security testing pipeline via Tekton.

Ensure that the necessary infrastructure has already been set up and installed as followed in [fyp-infra](https://github.com/ernestang98/fyp-infra). For more details on the actual security testing pipeline, refer to [fyp-infra](https://github.com/ernestang98/fyp-infra) under the `tekton` directory.

# Project Structure

```bash
└── chaos-testing
    ├── semgrep-manifests
    ├── defect-dojo-send-report.py
    └── sca-owasp-dependency-check.sh
```

# Semgrep Manifests (for SAST with semgrep)

In this directory, there is a collection of customised manifest files to be used by semgrep on top of the default rules it will use when performing static application security testing (SAST) during the first few stages of the pipeline to allow for customised linting and analysis of vulnerabilities from source code.

# Defect Dojo Script (for centralising testing reports)

`defect-dojo-send-report.py` is a python script which uses the defect-dojo API to send all generated reports during the security testing pipeline to defect dojo for subsequent vulnerability management.

# OWASP Dependency Check (for SCA)

Dependency-Check is a Software Composition Analysis (SCA) tool that attempts to detect publicly disclosed vulnerabilities contained within a project’s dependencies. It does this by determining if there is a Common Platform Enumeration (CPE) identifier for a given dependency. If found, it will generate a report linking to the associated CVE entries.