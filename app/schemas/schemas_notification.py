from datetime import date, datetime

from pydantic import BaseModel, Field


class Message(BaseModel):
    # A context represents a topic (ex: a loan),
    # there can only by one notification per context (ex: the loan should be returned, the loan is overdue or has been returned)
    context: str = Field(
        description="A context represents a topic. There can only by one notification per context."
    )
    # `firebase_device_token` is only contained in the database but is not returned by the API

    is_visible: bool = Field(
        description="A message can be visible or not, if it is not visible, it should only trigger an action"
    )

    title: str | None
    content: str | None

    action_module: str | None = Field(
        description="An identifier for the module that should be triggered when the notification is clicked"
    )
    action_table: str | None

    delivery_datetime: datetime | None = Field(
        description="The date the notification should be shown"
    )
    expire_on: date

    class Config:
        orm_mode = True


class FirebaseDevice(BaseModel):
    user_id: str = Field(description="The Hyperion user id")
    firebase_device_token: str = Field("Firebase device token")

    class Config:
        orm_mode = True
