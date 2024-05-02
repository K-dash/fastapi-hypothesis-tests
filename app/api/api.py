import uuid
from starlette import status

from app import app
from api.schema import (
    CreateUserSchema,
    GetUsersSchema,
    GetUserSchema,
)

USERS = []  # ユーザー保存用のインメモリリスト

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
    # 作成したユーザーをリストに追加
    USERS.append(user)
    return user
