from fastapi import APIRouter, Depends
from typing_extensions import Annotated

from src.accounts import schema
from src.accounts.persistance import AccountPersistenceManager

router = APIRouter(tags=["accounts"])

AccountPersistenceManagerDependency = Annotated[AccountPersistenceManager, Depends()]

@router.get(
    "/",
    description="Retrieve list of all accounts"
)
def list_accounts(manager: AccountPersistenceManagerDependency) -> schema.AccountsList:
    accounts = [acc.model_dump(mode="json") for acc in manager.list()]
    return schema.AccountsList.model_validate(accounts)

