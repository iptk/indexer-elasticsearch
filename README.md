# Elasticsearch Metadata Indexer
This metadata indexer lists all existing metadata in all datasets within a single dataset store and exports them to an Elasticsearch host.

## Usage
<a href="https://hub.docker.com/r/iptk/indexer-elasticsearch"><img src="https://img.shields.io/docker/build/iptk/indexer-elasticsearch.svg"></a>

Either use the *index.py* script directly, which requires Python 3.6 and the _elasticsearch_ and _iptk_ packages, or use the provided Docker image.

## Configuration
The Elasticsearch host can be configured through the *ELASTICSEARCH_HOST* environment variable, the dataset store location can be specified by *DATASETS_PATH*.
