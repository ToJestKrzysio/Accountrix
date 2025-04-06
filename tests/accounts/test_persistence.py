import random
import uuid
from decimal import Decimal
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest.mock import Mock

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
    with open(filepath, "w") as file:
        file.write(models.AccountsMap().model_dump_json())
    return AccountPersistenceManager(filepath)


def create_accounts_map(count: int = 3) -> models.AccountsMap:
    accounts = {}
    for idx in range(count):
        uuid_ = uuid.uuid4()
        account = models.Account(id=uuid_, username=f"user_{idx}", balance=Decimal((idx + 1) * 10))
        accounts[uuid_] = account
    return models.AccountsMap.model_validate(accounts)


def test_create_file_file_already_exists(filepath):
    instance = Mock(spec=AccountPersistenceManager)
    instance.filepath = filepath

    assert AccountPersistenceManager._create_file(instance) is False


def test_create_file_file_does_not_exists(directory):
    filepath = directory / "accounts_v2.json"
    instance = Mock(spec=AccountPersistenceManager)
    instance.filepath = filepath

    assert AccountPersistenceManager._create_file(instance) is True
    assert filepath.exists() is True


def test_create_happy_path(manager, filepath):
    account = models.Account(username="DogPool", balance=Decimal(42))
    result = manager.create(account)

    with filepath.open("r") as file:
        accounts = models.AccountsMap.model_validate_json(file.read())

    saved_account = accounts.root[result.id]
    assert len(accounts.root) == 1
    assert result == saved_account


def test_create_username_used(manager, filepath):
    account_1 = models.Account(username="DogPool", balance=Decimal(42))
    account_2 = models.Account(username="DogPool", balance=Decimal(42))

    account_1 = manager.create(account_1)
    with pytest.raises(
            exceptions.RecordCreateFailed,
            match=f"Account with username {account_2.username} already exists."
    ):
        manager.create(account_2)

    with filepath.open("r") as file:
        accounts = models.AccountsMap.model_validate_json(file.read())

    assert len(accounts.root) == 1
    assert account_1.id in accounts.root
    assert account_2.id not in accounts.root


def test_create_id_used(manager, filepath):
    uuid_ = uuid.uuid4()
    account_1 = models.Account(id=uuid_, username="DogPool", balance=Decimal(42))
    account_2 = models.Account(id=uuid_, username="UgandanKnuckles", balance=Decimal(42))

    account_1 = manager.create(account_1)
    account_2 = manager.create(account_2)

    with filepath.open("r") as file:
        accounts = models.AccountsMap.model_validate_json(file.read())

    assert account_1.id != account_2.id
    assert account_1.id in accounts.root
    assert account_2.id in accounts.root
    assert account_1 == accounts.root[account_1.id]
    assert account_2 == accounts.root[account_2.id]


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
    account = models.Account(username="DogPool", balance=Decimal(42))
    accounts.root[account.id] = account
    with filepath.open(mode="w") as file:
        file.write(accounts.model_dump_json())

    result = manager.get(account.id)

    assert result == account


def test_get_non_existing_account(manager, filepath):
    accounts = create_accounts_map(10)
    with filepath.open(mode="w") as file:
        file.write(accounts.model_dump_json())

    selected_id = uuid.uuid4()
    with pytest.raises(exceptions.RecordDoesNotExist):
        manager.get(selected_id)


def test_update_happy_path(manager, filepath):
    accounts = create_accounts_map(10)
    with filepath.open(mode="w") as file:
        file.write(accounts.model_dump_json())

    selected_id = random.choice(list(accounts.root.keys()))
    selected_account = accounts.root[selected_id]
    selected_account.balance = Decimal(123)
    selected_account.username = "UgandanKnuckles"

    result = manager.update(selected_id, selected_account)

    assert result == manager.get(selected_id)


def test_update_non_existing_account(manager, filepath):
    accounts = create_accounts_map(10)
    with filepath.open(mode="w") as file:
        file.write(accounts.model_dump_json())

    selected_id = uuid.uuid4()
    with pytest.raises(exceptions.RecordDoesNotExist):
        manager.update(selected_id, models.Account(username="404NotFound", balance=Decimal(106)))


def test_delete_happy_path(manager, filepath):
    accounts = create_accounts_map(10)
    with filepath.open(mode="w") as file:
        file.write(accounts.model_dump_json())

    selected_id = random.choice(list(accounts.root.keys()))
    manager.delete(selected_id)

    with filepath.open(mode="r") as file:
        accounts = models.AccountsMap.model_validate_json(file.read())

    assert selected_id not in accounts.root


def test_delete_non_existing_account(manager, filepath):
    accounts = create_accounts_map(10)
    with filepath.open(mode="w") as file:
        file.write(accounts.model_dump_json())

    selected_id = uuid.uuid4()
    with pytest.raises(exceptions.RecordDoesNotExist, match=f"Account with id {selected_id} does not exist"):
        manager.delete(selected_id)
