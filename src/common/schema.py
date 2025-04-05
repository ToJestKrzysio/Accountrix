from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Class representing simple message response from an API."""

    message: str
