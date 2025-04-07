from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, RootModel


class Account(BaseModel):
    """Model representing an account."""

    id: UUID
    username: str
    balance: Decimal


class AccountsList(RootModel):
    """Model representing a list of accounts."""

    root: list[Account]


class CreateAccountBody(BaseModel):
    """Model representing data required to create a new account."""

    username: str
    balance: Decimal


class UpdateAccountBody(BaseModel):
    """Model representing data required to perform a partial update of an account."""

    username: str | None = None
    balance: Decimal | None = None
