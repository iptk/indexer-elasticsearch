"""
Watches an IPTK HTTP API endpoint for new datasets and extracts DICOM metadata
if the dataset contains *.dcm files. If multiple dcm files are present in the
dataset, only one will be indexed.
"""

from json.decoder import JSONDecodeError
from elasticsearch import Elasticsearch
import requests
import sys
import os

api_endpoint = os.environ.get("API_ENDPOINT", "http://localhost").rstrip('/')
elasticsearch_host = os.environ.get("ELASTICSEARCH_HOST", "http://localhost").rstrip('/')
redis_host = os.environ.get("REDIS_HOST", None)
es = Elasticsearch(elasticsearch_host)

def index_metadata(dataset_id):
    dataset_url = f"{api_endpoint}/v3/datasets/{dataset_id}"
    meta_url = f"{dataset_url}/meta"
    metadatasets = requests.get(meta_url).json().get("metadatasets", [])
    for metadata_id in metadatasets:
        index_name = f"iptk-meta-{metadata_id}"
        metadata_url = f"{meta_url}/{metadata_id}"
        try:
            response = requests.get(metadata_url)
            metadata = response.json()
            es.index(index=index_name, doc_type="metadata", id=dataset_id, body=metadata)
        except Exception as e:
            print(f"Could not read metadata {metadata_id} for dataset {dataset_id}: {e}", file=sys.stderr)
            if response and response.text:
                print(response.text)
            return False
    return True

seen_ids = set() # Only try once per dataset
current_idx = 0
if redis_host:
    import redis
    r = redis.StrictRedis(redis_host, decode_responses=True)
    saved_idx = r.get("current_elasticsearch_index")
    if saved_idx:
        current_idx = saved_idx
print(f"Starting at index {current_idx}")

while True:
    params = {"start": current_idx, "per_page": 10}
    logs = requests.get(f"{api_endpoint}/v3/logs/dataset_changes", params=params).json()
    for entry in logs["entries"]:
        dataset_id = entry.get("dataset_id", None)
        if dataset_id not in seen_ids:
            index_metadata(dataset_id)
            seen_ids.add(dataset_id)
    current_idx = logs["range"]["end"]
    if redis_host:
        r.set("current_elasticsearch_index", current_idx)
    if logs["range"]["end"] == logs["range"]["max"]:
        time.sleep(10)
