import uuid
from decimal import Decimal

from pydantic import UUID4, BaseModel, Field, RootModel


class Account(BaseModel):
    """ Class representing an account. """
    id: UUID4 = Field(default_factory=lambda: uuid.uuid4())
    username: str
    balance: Decimal


class AccountsMap(RootModel):
    """ Class representing a list of accounts. """
    root: dict[UUID4, Account] = Field(default_factory=lambda: {})
