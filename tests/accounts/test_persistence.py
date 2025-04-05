import random
import uuid
from decimal import Decimal
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest

from src.accounts import models
from src.accounts.persistance import AccountPersistenceManager
from src.common import exceptions


@pytest.fixture
def directory():
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def filepath(directory):
    with NamedTemporaryFile(dir=directory, prefix="accounts", suffix=".json", mode="r+") as file:
        yield Path(file.name)


@pytest.fixture
def manager(filepath):
    return AccountPersistenceManager(filepath)


def create_accounts_map(count: int = 3) -> models.AccountsMap:
    accounts = {}
    for idx in range(count):
        uuid_ = uuid.uuid4()
        account = models.Account(id=uuid_, username=f"user_{idx}", balance=Decimal((idx + 1) * 10))
        accounts[uuid_] = account
    return models.AccountsMap.model_validate(accounts)


def test_list_happy_path(filepath, manager):
    accounts = create_accounts_map()
    with filepath.open(mode="w") as file:
        file.write(accounts.model_dump_json())

    result = manager.list()

    assert result == list(accounts.root.values())


def test_list_empty_input_map(filepath, manager):
    accounts = create_accounts_map(count=0)
    with filepath.open(mode="w") as file:
        file.write(accounts.model_dump_json())

    result = manager.list()

    assert result == []

def test_list_empty_input_file(directory):
    filepath = Path(directory) / "accounts_v2.json"
    manager = AccountPersistenceManager(filepath)
    result = manager.list()

    assert result == []


def test_get_happy_path(manager, filepath):
    accounts = create_accounts_map(10)
    with filepath.open(mode="w") as file:
        file.write(accounts.model_dump_json())

    selected_id = random.choice(list(accounts.root.keys()))
    result = manager.get(selected_id)

    assert result == accounts.root[selected_id]


def test_get_non_existing_account(manager, filepath):
    accounts = create_accounts_map(10)
    with filepath.open(mode="w") as file:
        file.write(accounts.model_dump_json())

    selected_id = uuid.uuid4()
    with pytest.raises(exceptions.RecordDoesNotExist):
        manager.get(selected_id)



