from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock
from uuid import UUID

import pytest

from src.accounts.persistance import AccountPersistenceManager
from src.main import app
from tests.accounts.factories import create_accounts_map


# As FastAPI check signature of dependency, mock implementation of persistence layer has to have exactly the same
# __init__ method which makes it quite hard to use Mock directly to replace overridden class
class MockAccountPersistenceManager:
    create = Mock()
    list = Mock()
    get = Mock()
    update = Mock()
    delete = Mock()

    def __init__(self, filepath: Path | None = None) -> None:
        self.filepath = filepath

    @classmethod
    def reset(cls):
        cls.create = Mock()
        cls.list = Mock()
        cls.get = Mock()
        cls.update = Mock()
        cls.delete = Mock()


@pytest.fixture
def override_persistence_manger():
    app.dependency_overrides[AccountPersistenceManager] = MockAccountPersistenceManager
    yield MockAccountPersistenceManager
    app.dependency_overrides = {}
    MockAccountPersistenceManager.reset()

def test_list_happy_path(client, override_persistence_manger):
    accounts = create_accounts_map()
    override_persistence_manger.list.return_value = list(accounts.root.values())

    response = client.get("/api/v1/accounts/")

    assert response.status_code == 200
    assert len(response.json()) == len(accounts.root)
    for acc in response.json():
        assert UUID(acc["id"]) in accounts.root
        account = accounts.root[UUID(acc["id"])]
        assert acc["username"] == account.username
        assert Decimal(acc["balance"]) == account.balance

def test_list_empty(client, override_persistence_manger):
    override_persistence_manger.list.return_value = []

    response = client.get("/api/v1/accounts/")

    assert response.status_code == 200
    assert len(response.json()) == 0