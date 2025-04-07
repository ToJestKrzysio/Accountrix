import uuid
from decimal import Decimal

from src.accounts import models


def create_accounts_map(count: int = 3) -> models.AccountsMap:
    accounts = {}
    for idx in range(count):
        uuid_ = uuid.uuid4()
        account = models.Account(id=uuid_, username=f"user_{idx}", balance=Decimal((idx + 1) * 10))
        accounts[uuid_] = account
    return models.AccountsMap.model_validate(accounts)
