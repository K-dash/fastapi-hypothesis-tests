import uuid
from uuid import UUID

from fastapi import HTTPException
from starlette import status
from starlette.responses import Response

from app import app
from api.schema import (
    CreateUserSchema,
    GetUsersSchema,
    GetUserSchema,
)

# 簡易的な保存用のインメモリのリスト
USERS = []

@app.get("/users", response_model=GetUsersSchema)
def get_users():
    return {"users": USERS}

@app.post("/users",
        status_code=status.HTTP_201_CREATED,
        response_model=GetUserSchema
)
def create_user(request_payload: CreateUserSchema):
    user = request_payload.model_dump()
    user["id"] = uuid.uuid4()
    USERS.append(user)
    return user

@app.get("/users/{user_id}", response_model=GetUserSchema)
def get_user(user_id: UUID):
    for user in USERS:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

@app.put("/users/{user_id}", response_model=GetUserSchema)
def update_user(user_id: UUID, request_payload: CreateUserSchema):
    for user in USERS:
        if user["id"] == user_id:
            user.update(request_payload.model_dump())
            return user
    raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID):
    for index, user in enumerate(USERS):
        if user["id"] == user_id:
            USERS.pop(index)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
