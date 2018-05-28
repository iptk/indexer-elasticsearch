"""
Lists all existing metadata in all datasets within a single dataset store and 
exports them to an Elasticsearch host. The Elasticsearch host can be configured
through the ELASTICSEARCH_HOST environment variable, the dataset store location
can be specified by DATASETS_PATH.
"""

from iptk import DatasetStore
from elasticsearch import Elasticsearch
import sys
import os
import re

elasticsearch_host = os.environ.get("ELASTICSEARCH_HOST", "http://localhost").rstrip('/')
datasets_path = os.environ.get("DATASETS_PATH", "/datasets")

es = Elasticsearch(elasticsearch_host)
ds = DatasetStore(datasets_path)

for dataset in ds.list_datasets():
    for spec_id in dataset.metadata_specs():
        if re.match("^[0-9a-z]{40}$", spec_id):
            index_name = f"iptk-meta-{spec_id}"
            ms = dataset.metadata_set(spec_id)
            metadata = dict(ms)
            es.index(index=index_name, doc_type="metadata", id=dataset.identifier, body=metadata)
