from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, RootModel


class Account(BaseModel):
    """Model representing an account."""

    id: UUID = Field(examples=["d5468285-dc82-40e8-8640-0f5c54aa01ed", "6bcc42b7-ab7d-443e-9372-45fb159c5532"])
    username: str = Field(examples=["DogPool", "Knuckles"])
    balance: Decimal = Field(examples=["0", "42"])


class AccountsList(RootModel):
    """Model representing a list of accounts."""

    root: list[Account]


class CreateAccountBody(BaseModel):
    """Model representing data required to create a new account."""

    username: str = Field(examples=["DogPool", "Knuckles"])
    balance: Decimal = Field(examples=["0", "42"])


class UpdateAccountBody(BaseModel):
    """Model representing data required to perform a partial update of an account."""

    username: str | None = Field(default=None, examples=["DogPool", "Knuckles"])
    balance: Decimal | None = Field(default=None, examples=["0", "42"])
