# Elasticsearch Metadata Indexer
This metadata indexer lists all existing metadata in all datasets within a single dataset store and exports them to an Elasticsearch host.

## Usage
<a href="https://hub.docker.com/r/iptk/indexer-elasticsearch"><img src="https://img.shields.io/docker/build/iptk/indexer-elasticsearch.svg"></a>

Either use the *index.py* script directly, which requires Python 3.6 and the _elasticsearch_ and _iptk_ packages, or use the provided Docker image.

## Configuration
The Elasticsearch host can be configured through the *ELASTICSEARCH_HOST* environment variable. The dataset store location can be specified by *DATASETS_PATH*.

If *SHUFFLE_DATASETS* is set, the script will generate a list of all datasets first, then shuffle that list and index datasets according to this order. This incurs additional startup time for iterating through the file system and generating the list, but ensures that all datasets have the same expected index time relative to the launch of the script. This is especially helpful when running multiple instances of the script to decrease the average index time.
