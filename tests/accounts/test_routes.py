from decimal import Decimal
from unittest.mock import Mock
from uuid import UUID

import pytest

from src.accounts import models, schema
from src.accounts.persistance import AccountPersistenceManager
from src.accounts.routes import get_account_persistence_manger
from src.common import exceptions
from src.main import app
from tests.accounts.factories import create_accounts_map


@pytest.fixture
def override_persistence_manger():
    manager = Mock(spec=AccountPersistenceManager)

    def mock_get_account_persistence_manger():
        return manager

    app.dependency_overrides[get_account_persistence_manger] = mock_get_account_persistence_manger
    yield manager
    app.dependency_overrides = {}


@pytest.fixture
def account():
    return models.Account(username="DogPool", balance=Decimal("42"))


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
    override_persistence_manger.list.assert_called_once_with()


def test_list_empty(client, override_persistence_manger):
    override_persistence_manger.list.return_value = []

    response = client.get("/api/v1/accounts/")

    assert response.status_code == 200
    assert len(response.json()) == 0
    override_persistence_manger.list.assert_called_once_with()


def test_get_happy_path(client, override_persistence_manger, account):
    override_persistence_manger.get.return_value = account

    response = client.get(f"/api/v1/accounts/{account.id}")

    assert response.status_code == 200
    assert response.json() == account.model_dump(mode="json")
    override_persistence_manger.get.assert_called_once_with(account.id)


def test_get_account_not_found(client, override_persistence_manger, account):
    override_persistence_manger.get.side_effect = exceptions.RecordDoesNotExist()

    response = client.get(f"/api/v1/accounts/{account.id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"
    override_persistence_manger.get.assert_called_once_with(account.id)


def test_create_account_happy_path(client, override_persistence_manger, account):
    override_persistence_manger.create.return_value = account

    response = client.post("/api/v1/accounts/", json=account.model_dump(mode="json"))

    assert response.status_code == 201
    assert response.json() == account.model_dump(mode="json")
    call_account = override_persistence_manger.create.call_args[0][0]
    assert call_account.username == account.username
    assert call_account.balance == account.balance


def test_create_account_record_create_failed(client, override_persistence_manger, account):
    error_msg = "Account with this parameters cannot be created."
    override_persistence_manger.create.side_effect = exceptions.RecordCreateFailed(error_msg)

    response = client.post("/api/v1/accounts/", json=account.model_dump(mode="json"))

    assert response.status_code == 409
    assert response.json()["detail"] == error_msg
    call_account = override_persistence_manger.create.call_args[0][0]
    assert call_account.username == account.username
    assert call_account.balance == account.balance


def test_replace_account_with_id_happy_path(client, override_persistence_manger, account):
    override_persistence_manger.update.return_value = account

    response = client.put(f"/api/v1/accounts/{account.id}/", json=account.model_dump(mode="json"))

    assert response.status_code == 200
    assert response.json() == account.model_dump(mode="json")
    override_persistence_manger.update.assert_called_once_with(account.id, account)


def test_replace_account_account_not_found(client, override_persistence_manger, account):
    override_persistence_manger.update.side_effect = exceptions.RecordDoesNotExist()

    response = client.put(f"/api/v1/accounts/{account.id}/", json=account.model_dump(mode="json"))

    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"
    override_persistence_manger.update.assert_called_once_with(account.id, account)


def test_replace_account_username_used(client, override_persistence_manger, account):
    error_msg = "Account cannot be updated using following payload."
    override_persistence_manger.update.side_effect = exceptions.RecordUpdateFailed(error_msg)

    response = client.put(f"/api/v1/accounts/{account.id}/", json=account.model_dump(mode="json"))

    assert response.status_code == 409
    assert response.json()["detail"] == error_msg
    override_persistence_manger.update.assert_called_once_with(account.id, account)


def test_update_account_by_id_happy_path(client, override_persistence_manger, account):
    new_account = schema.UpdateAccountBody(username="Dog Knuckles")
    result = models.Account(id=account.id, username="Dog Knuckles", balance=account.balance)

    override_persistence_manger.get.return_value = account
    override_persistence_manger.update.return_value = result

    response = client.patch(f"/api/v1/accounts/{account.id}/", json=new_account.model_dump(mode="json"))

    assert response.status_code == 200
    assert response.json() == result.model_dump(mode="json")
    override_persistence_manger.get.assert_called_once_with(account.id)
    override_persistence_manger.update.assert_called_once_with(account.id, result)


def test_update_account_by_id_account_not_found(client, override_persistence_manger, account):
    override_persistence_manger.get.side_effect = exceptions.RecordDoesNotExist()

    response = client.patch(f"/api/v1/accounts/{account.id}/", json=account.model_dump(mode="json"))

    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"
    override_persistence_manger.get.assert_called_once_with(account.id)
    assert override_persistence_manger.update.call_count == 0


def test_update_account_by_id_username_used(client, override_persistence_manger, account):
    new_account = schema.UpdateAccountBody(username="HamsterQuad")
    error_msg = "Account cannot be updated using following payload."
    merged = models.Account(id=account.id, username="HamsterQuad", balance=account.balance)

    override_persistence_manger.get.return_value = account
    override_persistence_manger.update.side_effect = exceptions.RecordUpdateFailed(error_msg)

    response = client.patch(f"/api/v1/accounts/{account.id}/", json=new_account.model_dump(mode="json"))

    assert response.status_code == 409
    assert response.json()["detail"] == error_msg
    override_persistence_manger.get.assert_called_once_with(account.id)
    override_persistence_manger.update.assert_called_once_with(account.id, merged)


def test_delete_account_by_id_happy_path(client, override_persistence_manger, account):
    override_persistence_manger.delete.return_value = None

    response = client.delete(f"/api/v1/accounts/{account.id}/")

    assert response.status_code == 204
    override_persistence_manger.delete.assert_called_once_with(account.id)


def test_delete_account_by_id_account_not_found(client, override_persistence_manger, account):
    override_persistence_manger.delete.side_effect = exceptions.RecordDoesNotExist

    response = client.delete(f"/api/v1/accounts/{account.id}/")

    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"
    override_persistence_manger.delete.assert_called_once_with(account.id)
