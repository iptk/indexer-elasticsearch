# Elasticsearch Metadata Indexer
This metadata indexer uses the IPTK web API to watch for new datasets through the */v3/logs/dataset_changes* endpoint. If a previously unseen dataset id is detected, the generator retrieves all available metadata sets using the */v3/datasets/<dataset_id>/meta* endpoint and indexes the metadata to an Elasticsearch host.

## Usage
<a href="https://hub.docker.com/r/iptk/indexer-elasticsearch"><img src="https://img.shields.io/docker/build/iptk/indexer-elasticsearch.svg"></a>
Either use the *index.py* script directly, which requires Python 3.6 and the _elasticsearch_ and _requests_ packages, or use the provided Docker image.

## Configuration
The API endpoint can be specified through the *API_ENDPOINT* environment variable. It must not contain the */v3/* version specification and may contain a username and password to make authenticated calls. A valid endpoint looks like this: *http://user:pass@api.server.com*. The Elasticsearch host can be configured through the *ELASTICSEARCH_HOST* variable and can be a raw hostname or an URL like the *API_ENDPOINT*. For details on the supported values, read the [elasticsearch-py documentation](https://elasticsearch-py.readthedocs.io/en/master/).