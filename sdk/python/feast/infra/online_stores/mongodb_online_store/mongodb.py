import warnings
from datetime import datetime
from typing import Optional, Sequence, Union, List, Tuple, Dict, Any, Callable

from pydantic import StrictStr

from feast import RepoConfig, FeatureView, Entity, utils
from feast.infra.key_encoding_utils import serialize_entity_key
from feast.infra.online_stores.helpers import compute_entity_id
from feast.infra.online_stores.online_store import OnlineStore
from feast.protos.feast.types.Value_pb2 import Value as ValueProto
from feast.protos.feast.types.EntityKey_pb2 import EntityKey as EntityKeyProto
from feast.repo_config import FeastConfigBaseModel
from pymongo import MongoClient


class MongoDBOnlineStoreConfig(FeastConfigBaseModel):
    """
    Configuration for the MongoDB online store.
    """
    connection_string: Optional[StrictStr] = None


class MongoDBOnlineStore(OnlineStore):
    """
    An online store implementation that uses MongoDB.
    """

    _client = None

    def _get_conn(self, config: RepoConfig, database_name: str, collection_name: str):
        """
        Obtain a connection to the MongoDB server and get the desired connection.
        """
        online_store_config = config.online_store
        assert isinstance(online_store_config, MongoDBOnlineStoreConfig)

        if not self._client:
            self._client = MongoClient(
                f"{online_store_config.connection_string or 'mongodb://localhost:27017/'}",
            )

        self.collection = self._client.get_database(database_name).get_collection(collection_name)

        return self.collection

    def online_write_batch(
        self,
        config: RepoConfig,
        table: FeatureView,
        data: List[
            Tuple[EntityKeyProto, Dict[str, ValueProto], datetime, Optional[datetime]]
        ],
        progress: Optional[Callable[[int], Any]],
    ) -> None:
        """
        Write a batch of feature rows to online MongoDB store.

        Note: This method applies a ``batch_writer`` to automatically handle any unprocessed items
        and resend them as needed, this is useful if you're loading a lot of data at a time.

        Args:
            config: The RepoConfig for the current FeatureStore.
            table: Feast FeatureView.
            data: A list of quadruplets containing Feature data. Each quadruplet contains an Entity Key,
            a dict containing feature values, an event timestamp for the document, and
            the created timestamp for the document if it exists.
            progress: Optional function to be called once every mini-batch of document is written to
            the online store. Can be used to display progress.
        """
        online_config = config.online_store
        assert isinstance(online_config, MongoDBOnlineStoreConfig)

        batch = []
        for entity_key, features, timestamp, created_ts in data:
            batch.append(_create_feature_document(config, entity_key, features, timestamp, created_ts))
        self._client[table.name].insert_many(batch)

    def online_read(
        self,
        config: RepoConfig,
        table: FeatureView,
        entity_keys: List[EntityKeyProto],
        requested_features: Optional[List[str]] = None,
    ) -> List[Tuple[Optional[datetime], Optional[Dict[str, ValueProto]]]]:
        """
        Read feature values that map to the requested entities from the online store.

        Args:
            config: The RepoConfig for the current FeatureStore.
            table: Feast FeatureView.
            entity_keys: a list of entity keys that should be read
                         from the FeatureStore.
            requested_features: Optional list of feature names to read.
        """
        warnings.warn(
            "This online store is an experimental feature in alpha development. "
            "Some functionality may still be unstable so functionality can change in the future.",
            RuntimeWarning,
        )
        project = config.project

        collection = self._get_conn(config, project, table.name)

        entity_ids = _to_entity_ids(config, entity_keys)
        result: List[Tuple[Optional[datetime], Optional[Dict[str, Any]]]] = []
        for entity_key in entity_keys:
            features_to_project = {feature: 1 for feature in requested_features}
            if features_to_project:
                features_to_project["event_ts"] = 1
                docs = collection.find({entity_key: {"$exists": True}}, features_to_project)
            else:
                docs = collection.find({entity_key: {"$exists": True}})
            for doc in docs:
                value = ValueProto()
                value.ParseFromString(doc)
                result.append((doc.get("event_ts"), value))
        return result


    def update(
            self,
            config: RepoConfig,
            tables_to_delete: Sequence[FeatureView],
            tables_to_keep: Sequence[FeatureView],
            entities_to_delete: Sequence[Entity],
            entities_to_keep: Sequence[Entity],
            partial: bool,
    ):
        """
        Update DB schema, creating and dropping collections accordingly.

        Args:
            config: The RepoConfig for the current FeatureStore.
            tables_to_delete: Collections to delete from the OnlineStore.
            tables_to_keep: Collections to keep in the OnlineStore.
        """
        warnings.warn(
            "This online store is an experimental feature in alpha development. "
            "Some functionality may still be unstable so functionality can change in the future.",
            RuntimeWarning,
        )
        project = config.project

        for coll in tables_to_keep:
            self._client[project].create_collection(coll.name)
        for coll in tables_to_delete:
            self._client[project].drop_collection(coll.name)

    def teardown(
            self,
            config: RepoConfig,
            tables: Sequence[FeatureView],
            entities: Sequence[Entity],
    ):
        """
        Teardown the DB, deleting collections accordingly.

        Args:
            config: The RepoConfig for the current FeatureStore.
            tables: Tables to delete from the feature repo.
        """
        warnings.warn(
            "This online store is an experimental feature in alpha development. "
            "Some functionality may still be unstable so functionality can change in the future.",
            RuntimeWarning,
        )
        project = config.project

        for coll in tables:
            self._client[project].drop_collection(coll.name)

def _create_feature_document(config, entity_key, features, created_ts, timestamp):
    entity_id = compute_entity_id(
        entity_key,
        entity_key_serialization_version=config.entity_key_serialization_version,
    )
    return {
        "entity_id": entity_id,
        "event_ts": str(utils.make_tzaware(timestamp)),
        "event_created_ts": str(utils.make_tzaware(created_ts)),
        "values": {
            k: v.SerializeToString()
            for k, v in features.items()
        },
    }

def _to_entity_ids(config: RepoConfig, entity_keys: List[EntityKeyProto]):
    return [
        compute_entity_id(
            entity_key,
            entity_key_serialization_version=config.entity_key_serialization_version,
        )
        for entity_key in entity_keys
    ]
