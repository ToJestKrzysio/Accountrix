import os
from logging import getLogger
from pathlib import Path
from uuid import UUID, uuid4

from src.accounts import models
from src.common import exceptions

logger = getLogger(__name__)


class AccountPersistenceManager:

    def __init__(self, filepath: Path | None = None):
        default_filepath = Path(os.getcwd()).parent.parent / "data" / "accounts.json"
        self.filepath = filepath or default_filepath
        self._create_file_in_not_exists()

    def _create_file_in_not_exists(self):
        """ Checks whether file exists, if not creates new file to store data in. """
        if self.filepath.exists():
            return

        with self.filepath.open(mode="w") as file:
            file.write(models.AccountsMap().model_dump_json())


    def _load(self) -> models.AccountsMap:
        """ Load accounts data from file. """
        logger.debug("Loading accounts data")
        with self.filepath.open("r") as file:
            accounts = models.AccountsMap.model_validate_json(file.read())
            logger.debug("Loaded accounts data")
            return accounts

    def _save(self, accounts: models.AccountsMap) -> None:
        """ Save accounts data to file. """
        logger.debug("Saving accounts data")
        with self.filepath.open("w") as file:
            file.write(accounts.model_dump_json())
        logger.debug("Saved accounts data")

    def list(self) -> list[models.Account]:
        """ Retrieve list of all accounts. """
        logger.debug("Retrieving accounts list")
        accounts_map = self._load()
        accounts = list(accounts_map.root.values())
        logger.debug(f"Retrieved {len(accounts)} accounts")
        return accounts

    def get(self, account_id: UUID) -> models.Account:
        """ Retrieve an account by identifier  """
        logger.debug(f"Retrieving account {account_id}")
        accounts = self._load()

        if account_id not in accounts.root:
            msg = f"Account with id {account_id} does not exist"
            logger.error(msg)
            raise exceptions.RecordDoesNotExist(msg)

        account = accounts.root[account_id]
        logger.debug(f"Account with id {account.id} found")
        return account

    def update(self, account_id: str, account: models.Account) -> models.Account:
        """ Set record with id to newly provided value. """
        logger.debug(f"Updating account with id {account_id} using payload {account}")
        accounts = self._load()

        if account_id not in accounts.root:
            msg = f"Account with id {account_id} does not exist"
            logger.error(msg)
            raise exceptions.RecordDoesNotExist(msg)

        account.id = UUID(account_id)
        accounts.root[account_id] = account
        self._save(accounts)
        logger.debug(f"Account with id {account_id} was updated")
        return account


    def delete(self, account_id: str) -> None:
        """ Delete account by provided id. """
        logger.debug(f"Deleting account with id {account_id}")
        accounts = self._load()

        if account_id not in accounts.root:
            msg = f"Account with id {account_id} does not exist"
            logger.error(msg)
            raise exceptions.RecordDoesNotExist(msg)

        del accounts.root[account_id]
        self._save(accounts)
        logger.debug(f"Account with id {account_id} was deleted")

    def create(self, account: models.Account) -> models.Account:
        """ Create new account with provided payload. """
        logger.debug(f"Creating new account with payload {account}")
        accounts = self._load()

        for existing_account in accounts.root.values():
            if existing_account.username == account.username:
                raise exceptions.RecordCreateFailed(f"Account with username {account.username} already exists.")

        retries = 0
        while account.id in accounts.root and retries < 10:
            logger.warning(f"Account id already in use: {account.id}. Generating a new one.")
            if retries >= 5:
                msg = "Failed to assigning valid account id"
                logger.error(msg)
                raise exceptions.RecordCreateFailed(msg)

            account.id = uuid4()
            retries += 1

        accounts.roor[account.id] = account
        self._save(accounts)
        logger.debug(f"Account with id {account.id} was created")
        return account

