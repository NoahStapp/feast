from tests.integration.feature_repos.integration_test_repo_config import (
    IntegrationTestRepoConfig,
)

FULL_REPO_CONFIGS = [
    IntegrationTestRepoConfig(
        online_store="mongodb"
    ),
]

AVAILABLE_ONLINE_STORES = {"mongodb": ({"type": "mongodb", "connection_string": "mongodb://localhost:27017"}, None)}
