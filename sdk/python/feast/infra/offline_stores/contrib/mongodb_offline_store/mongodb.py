from datetime import datetime
from typing import List, Optional

from feast import RepoConfig
from feast.data_source import DataSource
from feast.infra.offline_stores.offline_store import OfflineStore, RetrievalJob


class MongoDBOfflineStore(OfflineStore):
    def pull_latest_from_table_or_query(
        self,
        config: RepoConfig,
        data_source: DataSource,
        join_key_columns: List[str],
        feature_name_columns: List[str],
        timestamp_field: str,
        created_timestamp_column: Optional[str],
        start_date: datetime,
        end_date: datetime,
    ) -> RetrievalJob:
        ...



class MongoDBRetrievalJob(RetrievalJob):
    def __init__(self, data_source: DataSource, query: str):
        self.data_source = data_source
        self.query = query

    def to_df(self):
        # Only execute the evaluation function to build the final historical retrieval dataframe at the last moment.
        print("Getting a pandas DataFrame from a File is easy!")
        df = self.evaluation_function()
        return df

    def to_arrow(self):
        # Only execute the evaluation function to build the final historical retrieval dataframe at the last moment.
        print("Getting a pandas DataFrame from a File is easy!")
        df = self.evaluation_function()
        return pyarrow.Table.from_pandas(df)

    def to_remote_storage(self):
        # Optional method to write to an offline storage location to support scalable batch materialization.
        pass

