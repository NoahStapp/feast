from typing import Dict

from testcontainers.core.waiting_utils import wait_for_logs, wait_container_is_ready
from testcontainers.mongodb import MongoDbContainer

from tests.integration.feature_repos.universal.online_store_creator import (
    OnlineStoreCreator,
)


class MongoDBOnlineStoreCreator(OnlineStoreCreator):
    def __init__(self, project_name: str, **kwargs):
        super().__init__(project_name)
        self.container = MongoDbContainer()

    def create_online_store(self) -> Dict[str, str]:
        self.container.start()
        log_string_to_wait_for = (
            "Waiting for connections"
        )

        wait_for_logs(
            container=self.container, predicate=log_string_to_wait_for, timeout=10
        )

        return {
            "type": "mongodb",
            "connection_string": self.container.get_connection_url(),
        }

    def teardown(self):
        self.container.stop()
