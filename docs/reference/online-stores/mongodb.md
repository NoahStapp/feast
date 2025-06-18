# MongoDB online store

## Description

The [MongoDB](https://www.mongodb.com/) online store provides support for materializing feature values into MongoDB.

## Getting started
In order to use this online store, you'll need to install the MongoDB extra (along with the dependency needed for the offline store of choice). E.g.

`pip install 'feast[mongodb]'`

You can get started by using any of the other templates (e.g. `feast init -t gcp` or `feast init -t snowflake` or `feast init -t aws`), and then swapping in MongoDB as the online store as seen below in the examples.

## Examples

Connecting to a local MongoDB instance without SSL or authentication:

{% code title="feature_store.yaml" %}
```yaml
project: my_feature_repo
registry: data/registry.db
provider: local
online_store:
  type: mongodb
  path: "data/online_store.db"
  connection_string: "mongodb://localhost:27017/"
```
{% endcode %}


The full set of configuration options is available in [MongoDBOnlineStoreConfig](https://rtd.feast.dev/en/latest/#feast.infra.online_stores.nongodb.MongoDBOnlineStoreConfig).

## Functionality Matrix

The set of functionality supported by online stores is described in detail [here](overview.md#functionality).
Below is a matrix indicating which functionality is supported by the MongoDB online store.

|                                                           | MongoDB |
|:----------------------------------------------------------|:--------|
| write feature values to the online store                  | yes     |
| read feature values from the online store                 | yes     |
| update infrastructure (e.g. tables) in the online store   | yes     |
| teardown infrastructure (e.g. tables) in the online store | yes     |
| generate a plan of infrastructure changes                 | no      |
| support for on-demand transforms                          | yes     |
| readable by Python SDK                                    | yes     |
| readable by Java                                          | no      |
| readable by Go                                            | no      |
| support for entityless feature views                      | yes     |
| support for concurrent writing to the same key            | yes     |
| support for ttl (time to live) at retrieval               | yes     |
| support for deleting expired data                         | yes     |
| collocated by feature view                                | yes     |
| collocated by feature service                             | no      |
| collocated by entity key                                  | yes     |
| vector similarity search                                  | no      |

To compare this set of functionality against other online stores, please see the full [functionality matrix](overview.md#functionality-matrix).
