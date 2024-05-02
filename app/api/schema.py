from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, conint, field_validator
from typing import ClassVar, Dict

class UserProfileSchema(BaseModel):
    name: str
    age: Optional[conint(ge=0, le=120, strict=True)] # type: ignore
    email: EmailStr

    @field_validator("age")
    def age_non_nullable(cls, value):
        """ageはOptional項目だが、null は許容しない"""
        assert value is not None, "age may not be None"
        return value

    Config: ClassVar[Dict[str, any]] = {
        "extra": "forbid",  # UserProfileSchemaに定義していない項目は受け付けない
    }

class CreateUserSchema(BaseModel):
    profile: UserProfileSchema

    Config: ClassVar[Dict[str, any]] = {
        "extra": "forbid", # CreateUserSchemaに定義していない項目は受け付けない
    }

class GetUserSchema(CreateUserSchema):
    id: UUID
    lastupdated: datetime = datetime.now(ZoneInfo("Asia/Tokyo"))

class GetUsersSchema(BaseModel):
    users: List[GetUserSchema]
