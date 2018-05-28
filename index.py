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
    

def handle_dataset(dataset_id):
    dataset_url = f"{api_endpoint}/v3/datasets/{dataset_id}"
    meta_response = requests.get(f"{dataset_url}/meta")
    try:
        meta_info = meta_response.json()
    except JSONDecodeError:
        print(meta_response.status_code)
    if spec_id in meta_info["metadatasets"]:
        return
    file_list = requests.get(f"{dataset_url}/data").json()
    dicom_files = [x for x in file_list["files"] if x.endswith(".dcm")]
    if not dicom_files:
        return
    dicom_file = dicom_files[0]
    dicom_data = requests.get(f"{dataset_url}/data/{dicom_file}").content
    ds = pydicom.read_file(io.BytesIO(dicom_data))
    ds.remove_private_tags()
    tags = ds.keys()
    info = {}
    for element in ds.values():
        if not element.keyword:
            # Ignore private and unknown elements
            continue
        if element.VM > 1:
            # Ignore elements with multiple values
            continue
        if element.VR == "DA":
            # For date elements, try to join them with the corresponding time
            # element to create an additional DateTime element.
            first_part = element.keyword[:-4]
            time_keyword = first_part + "Time"
            time_value = ds.get(time_keyword, "000000.0")
            if '.' not in time_value:
                time_value = time_value + '.0'
            date_value = element.value
            full_value = f"{date_value} {time_value}"
            try:
                date_time = datetime.strptime(full_value, '%Y%m%d %H%M%S.%f')
                info[first_part + "DateTime"] = date_time.isoformat()
            except ValueError:
                # If date or time were not properly formatted, ignore.
                pass
        if element.VR == "PN":
            info[element.keyword] = str(element.value)
        if element.VR in ["US", "DS", "UI", "CS", "IS", "LO", "SH", "TM", "DA"]:
            info[element.keyword] = element.value
    dicom_meta_url = f"{dataset_url}/meta/{spec_id}"
    r = requests.post(dicom_meta_url, json=info)
    print(f"Dataset {dataset_id} updated ({r.status_code})")

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
