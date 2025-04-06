from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, RootModel


class Account(BaseModel):
    """ Model representing user data"""
    id: UUID
    username: str
    balance: Decimal


AccountsList = RootModel[list[Account]]
