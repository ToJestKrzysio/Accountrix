from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from typing_extensions import Annotated

from src.accounts import models, schema
from src.accounts.persistance import AccountPersistenceManager
from src.common import exceptions
from src.common.schema import ErrorResponse

router = APIRouter(tags=["accounts"])


def get_account_persistence_manger():
    return AccountPersistenceManager()


AccountPersistenceManagerDependency = Annotated[AccountPersistenceManager, Depends(get_account_persistence_manger)]


@router.get(
    "/",
    description="Retrieve list of all accounts",
)
def list_accounts(manager: AccountPersistenceManagerDependency) -> schema.AccountsList:
    accounts = [acc.model_dump(mode="json") for acc in manager.list()]
    return schema.AccountsList.model_validate(accounts)


@router.get(
    "/{account_id}/",
    description="Retrieve a specific account by id",
    responses={
        404: {"model": ErrorResponse},
    },
)
def get_account_by_id(manager: AccountPersistenceManagerDependency, account_id: UUID) -> schema.Account:
    try:
        account = manager.get(account_id)
    except exceptions.RecordDoesNotExist:
        raise HTTPException(status_code=404, detail="Account not found")

    return schema.Account.model_validate(account.model_dump())


@router.post(
    "/",
    description="Create a new account",
    status_code=201,
    responses={
        409: {"model": ErrorResponse},
    },
)
def create_new_account(
    manager: AccountPersistenceManagerDependency, account_data: schema.CreateAccountBody
) -> schema.Account:
    account = models.Account.model_validate(account_data.model_dump())
    try:
        new_account = manager.create(account)
    except exceptions.RecordCreateFailed as err:
        raise HTTPException(status_code=409, detail=str(err))

    return schema.Account.model_validate(new_account.model_dump())


@router.put(
    "/{account_id}/",
    description="Update account specified by id, will perform replace of entire record.",
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def replace_account_with_id(
    manager: AccountPersistenceManagerDependency, account_id: UUID, account_data: schema.CreateAccountBody
) -> schema.Account:
    account = models.Account.model_validate({**account_data.model_dump(), "id": account_id})
    try:
        updated_account = manager.update(account_id, account)
    except exceptions.RecordDoesNotExist:
        raise HTTPException(status_code=404, detail="Account not found")
    except exceptions.RecordUpdateFailed as err:
        raise HTTPException(status_code=409, detail=str(err))

    return schema.Account.model_validate(updated_account.model_dump())


@router.patch(
    "/{account_id}/",
    description="Update account specified by id, will update only provided fields.",
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def update_account_by_id(
    manager: AccountPersistenceManagerDependency, account_id: UUID, account_data: schema.UpdateAccountBody
) -> schema.Account:
    try:
        old_account = manager.get(account_id)
    except exceptions.RecordDoesNotExist:
        raise HTTPException(status_code=404, detail="Account not found")

    merged_data = {**old_account.model_dump(), **account_data.model_dump(exclude_defaults=True)}
    account = models.Account.model_validate(merged_data)

    try:
        updated_account = manager.update(account_id, account)
    except exceptions.RecordDoesNotExist:
        raise HTTPException(status_code=404, detail="Account not found")
    except exceptions.RecordUpdateFailed as err:
        raise HTTPException(status_code=409, detail=str(err))

    return schema.Account.model_validate(updated_account.model_dump())


@router.delete(
    "/{account_id}/",
    description="Delete account with specified id.",
    status_code=204,
    responses={
        404: {"model": ErrorResponse},
    },
)
def delete_account_by_id(
    manager: AccountPersistenceManagerDependency,
    account_id: UUID,
):
    try:
        manager.delete(account_id)
    except exceptions.RecordDoesNotExist:
        raise HTTPException(status_code=404, detail="Account not found")
