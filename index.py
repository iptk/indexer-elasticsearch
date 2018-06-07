"""
Lists all existing metadata in all datasets within a single dataset store and 
exports them to an Elasticsearch host. The Elasticsearch host can be configured
through the ELASTICSEARCH_HOST environment variable, the dataset store location
can be specified by DATASETS_PATH.
"""

from iptk import DatasetStore
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
import sys
import os
import re

elasticsearch_host = os.environ.get("ELASTICSEARCH_HOST", "http://localhost").rstrip('/')
datasets_path = os.environ.get("DATASETS_PATH", "/datasets")
shuffle_datasets = "SHUFFLE_DATASETS" in os.environ

es = Elasticsearch(elasticsearch_host)
ds = DatasetStore(datasets_path)
datasets = ds.list_datasets()

if shuffle_datasets:
    datasets = list(datasets)
    shuffle(datasets)
    
for dataset in datasets:
    for spec_id in dataset.metadata_specs():
        if re.match("^[0-9a-z]{40}$", spec_id):
            index_name = f"iptk-meta-{spec_id}"
            ms = dataset.metadata_set(spec_id)
            metadata = dict(ms)
            try:
                es.index(index=index_name, doc_type="metadata", id=dataset.identifier, body=metadata)
            except RequestError:
                # Issue a warning if indexing fails, keep going.
                print(f"Could not index metadata {spec_id} for dataset {dataset.identifier}", file=sys.stderr)
                pass