import os
import json
from datetime import datetime, timedelta
from typing import Dict, List
import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-ds', help='File path for semgrep report from default rules', required=False)
parser.add_argument('-dc', help='File path for dependency check report', required=False)
parser.add_argument('-ss', help='File path for sonarscan report', required=False)
parser.add_argument('-cs', help='File path for semgrep report from custom rules', required=False)
parser.add_argument('-t',  help='File path for trivy report', required=False)
parser.add_argument('-c',  help='File path for checkov report', required=False)
parser.add_argument('-z',  help='File path for zap report', required=False)
parser.add_argument('-i',  help='Host of DefectDojo', required=True)
parser.add_argument('-p',  help='Port of DefectDojo', required=True)
parser.add_argument('-pa',  help='Password of DefectDojo', required=True)

class SendScans:
    def __init__(self, defectdojo_host: str, defectdojo_user: str, defectdojo_password: str):
        self.defectdojo_host = defectdojo_host
        self.defectdojo_user = defectdojo_user
        self.defectdojo_password = defectdojo_password
        self.defectdojo_api_key = self.__get_defectdojo_api_key()
        self.product_id = None
        self.engagement_id = None
        self.start_date = None
        self.end_date = None

    def __get_defectdojo_api_key(self) -> str:
        try:
            url = f"{self.defectdojo_host}/api/v2/api-token-auth/"
            payload = json.dumps({"username": self.defectdojo_user, "password": self.defectdojo_password})
            headers = {"Accept": "application/json", "Content-Type": "application/json"}
            response = requests.request("POST", url, headers=headers, data=payload)
            response.raise_for_status()
            return response.json()["token"]
        except requests.exceptions.HTTPError as e:
            print(f"Failed to get API key: {e}")
            raise e

    def __product_exists(self, product_name: str) -> int:
        url = f"{self.defectdojo_host}/api/v2/products/?name={product_name}"
        headers = {"Accept": "application/json", "Authorization": f"Token {self.defectdojo_api_key}"}
        try:
            response = requests.request("GET", url, headers=headers)
            response.raise_for_status()
            if len(response.json()["results"]) == 0:
                return None
            return response.json()["results"][0]["id"]
        except requests.exceptions.RequestException as e:
            print(f"Failed to get product: {e}")
            raise e

    def create_product(self, product_name: str, product_description: str, product_type: int) -> None:
        self.product_id = self.__product_exists(product_name)
        if self.product_id is None:
            url = f"{self.defectdojo_host}/api/v2/products/"
            payload = json.dumps({"name": product_name, "description": product_description, "prod_type": product_type})
            headers = {"Accept": "application/json", "Authorization": f"Token {self.defectdojo_api_key}", "Content-Type": "application/json"}
            try:
                response = requests.request("POST", url, headers=headers, data=payload)
                response.raise_for_status()
                self.product_id = response.json()["id"]
                print(f"Created product {self.product_id}")
            except requests.exceptions.HTTPError as e:
                print(f"Failed to create product: {e}")
                raise e

    def create_engagement(
        self,
        pipeline_id: str,
        commit_hash: str,
        branch_or_tag: str,
        version: str,
        repo_uri: str,
        scm_server: int,
        build_server: int,
        engagement_duration_days: int,
    ) -> None:
        url = f"{self.defectdojo_host}/api/v2/engagements/"
        self.start_date = datetime.now().strftime("%Y-%m-%d")
        self.end_date = (datetime.now() + timedelta(days=engagement_duration_days)).strftime("%Y-%m-%d")
        payload = json.dumps(
            {
                "product": self.product_id,
                "target_start": self.start_date,
                "target_end": self.end_date
            }
        )
        headers = {"Accept": "application/json", "Authorization": f"Token {self.defectdojo_api_key}", "Content-Type": "application/json"}
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            response.raise_for_status()
            self.engagement_id = response.json()["id"]
            print(f"Created engagement {self.engagement_id}")
        except requests.exceptions.HTTPError as e:
            print(f"Failed to create engagement: {e}")
            raise e

    def upload_scans(self, scans: List[Dict[str, str]]) -> None:
        for scan in scans:
            url = f"{self.defectdojo_host}/api/v2/import-scan/"
            payload = {
                "scan_date": self.start_date,
                "engagement": self.engagement_id,
                "scan_type": scan["scan_type"],
                "active": "true",
                "verified": "false",
                #"close_old_findings": "true",
                "skip_duplicates": "true",
                "minimum_severity": "Info",
            }
            try:
                file = {"file": open(scan["scan_file"], "rb")}
            except Exception as e:
                print(f"Failed to open scan file {scan['scan_file']}: {e}")
                continue
            headers = {"Accept": "application/json", "Authorization": f"Token {self.defectdojo_api_key}"}
            try:
                response = requests.request("POST", url, headers=headers, data=payload, files=file)
                response.raise_for_status()
                print(f"Uploaded scan {scan['scan_file']}")
            except requests.exceptions.HTTPError as e:
                print(f"Failed to upload scan {scan['scan_file']}: {e}")
                continue

def main():
    args = parser.parse_args()

    DEFECTDOJO_HOST = os.getenv("DEFECTDOJO_HOST", f"http://{args.i}:{args.p}")
    DEFECTDOJO_USER = os.getenv("DEFECTDOJO_USER", "admin")
    DEFECTDOJO_PASSWORD = os.getenv("DEFECTDOJO_PASSWORD", f"{args.pa}")
    send_scans = SendScans(DEFECTDOJO_HOST, DEFECTDOJO_USER, DEFECTDOJO_PASSWORD)
    PRODUCT = os.getenv("CI_PROJECT_TITLE", f"ASR System Security Test #{str(datetime.now().strftime('%s'))}")
    send_scans.create_product(PRODUCT, PRODUCT, 1)  # 1 - Research and Development, product type
    PIPELINE_ID = os.getenv("CI_PIPELINE_ID", "1")
    VERSION = os.getenv("VERSION", "1")
    if VERSION is None:
        VERSION = os.getenv("CI_COMMIT_SHORT_SHA", "1")
    COMMIT_HASH = os.getenv("CI_COMMIT_SHA", "hash")
    BRANCH_OR_TAG = os.getenv("CI_COMMIT_REF_NAME", "branch")
    REPO_URI = os.getenv("CI_PROJECT_URL", "https://github.com/ntuspeechlab/asr-client-scripts")
    SCM_SERVER = 1
    BUILD_SERVER = 2
    ENGAGEMENT_DURATION_DAYS = 1  # Medium Finding SLA Days + 10
    send_scans.create_engagement(PIPELINE_ID, COMMIT_HASH, BRANCH_OR_TAG, VERSION, REPO_URI, SCM_SERVER, BUILD_SERVER, ENGAGEMENT_DURATION_DAYS)

    scans = []
    
    default_semgrep_rules_report = args.ds
    if default_semgrep_rules_report != None:
        scans.append({"scan_type": "Semgrep JSON Report", "scan_file": default_semgrep_rules_report})
    
    custom_semgrep_rules_report = args.cs
    if custom_semgrep_rules_report != None:
        scans.append({"scan_type": "Semgrep JSON Report", "scan_file": custom_semgrep_rules_report})

    trivy_report = args.t
    if trivy_report != None:
        scans.append({"scan_type": "Trivy Scan", "scan_file": trivy_report})    

    checkov_report = args.c
    if checkov_report != None:
        scans.append({"scan_type": "Checkov Scan", "scan_file": checkov_report})    

    zap_report = args.z
    if zap_report != None:
        scans.append({"scan_type": "ZAP Scan", "scan_file": zap_report})    

    dependency_check_report = args.dc
    if dependency_check_report != None:
        scans.append({"scan_type": "Dependency Check Scan", "scan_file": dependency_check_report})  

    sonarscan_report = args.ss
    if dependency_check_report != None:
        scans.append({"scan_type": "SonarQube Scan detailed", "scan_file": sonarscan_report})  

    if len(scans) > 0:
        send_scans.upload_scans(scans)   


if __name__ == "__main__":
    main()


