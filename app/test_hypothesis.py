from pathlib import Path

import hypothesis.strategies as st
import jsonschema
import yaml
from fastapi.testclient import TestClient
from hypothesis import given, Verbosity, settings
from jsonschema import ValidationError, RefResolver

from app import app

# OpenAPI仕様(openapi.yaml)を読み込む
users_api_spec = yaml.full_load(
    (Path(__file__).parent / "openapi.yaml").read_text()
)

# OpenAPI仕様の中で、POSTリクエスト/レスポンスの定義が記述されているポインタをそれぞれ取得
# リクエストペイロード用
create_user_schema = users_api_spec["components"]["schemas"]["CreateUserSchema"]
# レスポンスペイロード用
get_user_schema = users_api_spec["components"]["schemas"]["GetUserSchema"]

def is_valid_payload(payload, schema):
    """引数に渡されたペイロードがAPI仕様に準拠しているかどうか検証するためのヘルパー関数"""
    try:
        # 検証はjsonschemaのvalidate関数を使う
        jsonschema.validate(
            payload, schema=schema,
            resolver=RefResolver("", users_api_spec)
        )
    except ValidationError as e:
        print(f"Validation error: {e.message}")
        return False
    else:
        print(f"Validation successful: {payload}")
        return True

test_client = TestClient(app=app)

# リクエストペイロードがとり得るすべての値を定義
values_strategy = (
        st.none() |
        st.text() |
        st.integers() |
        st.emails()
)

# テスト用のペイロードを作成
# 1. keyは固定でvalueは動的に生成するストラテジ
random_value_strategy = st.fixed_dictionaries(
    {
        "name": values_strategy,
        "age": values_strategy,
        "email": values_strategy
    }
)

# 2. keyとvalueの両方を動的に生成するストラテジ
random_key_value_strategy = st.dictionaries(
    keys=st.sampled_from(["name", "age", "email", "invalid_field"]),
    values=values_strategy,
    min_size=0,
    max_size=4
)

# 3. 期待値を含めたストラテジ
expected_key_value_strategy = st.fixed_dictionaries(
    {
        "name": st.text(min_size=1),
        "age": st.integers(min_value=0, max_value=120),
        "email": st.emails()
    }
)

# 1,2,3を結合したストラテジを定義
strategy = st.fixed_dictionaries({"profile": random_value_strategy}) | \
           st.fixed_dictionaries({"profile": random_key_value_strategy}) | \
           st.fixed_dictionaries({"profile": expected_key_value_strategy})


# settignsでテストケースの実行回数を指定
@settings(verbosity=Verbosity.verbose, max_examples=1000)
# given() に作成したストラテジを注入
@given(strategy)
def test_post(request_payload): # request_payloadにはストラテジが生成した値が渡される
    # POST /usersエンドポイントへテスト実行
    response = test_client.post("/users", json=request_payload)
    # リクエストペイロードがOpenAPI仕様に準拠しているかどうかを判断
    if is_valid_payload(request_payload, create_user_schema):
        assert response.status_code == 201
        # リクエストが正しい場合、レスポンスペイロードがOpenAPI仕様に準拠しているかどうかを判断
        assert is_valid_payload(response.json(), get_user_schema)
    else:
        assert response.status_code == 422
