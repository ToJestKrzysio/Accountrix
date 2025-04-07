from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """ Class representing simple message response from an API. """
    message: str = Field(examples=["Ok", "Everything is fine."])


class ErrorResponse(BaseModel):
    """ Class representing error response from an API. """
    detail: str = Field(examples=["Cause of failure."])

