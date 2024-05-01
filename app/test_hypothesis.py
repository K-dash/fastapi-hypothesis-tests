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

# API仕様の中の CreateUserSchema のポインタを取得
create_user_schema = users_api_spec["components"]["schemas"]["CreateUserSchema"]

# リクエストペイロードがAPI仕様に準拠しているかどうかを判断するためのヘルパー関数
def is_valid_payload(payload, schema):
    try:
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
# keyは固定でvalueは動的に生成するストラテジー
random_value_strategy = st.fixed_dictionaries(
    {
        "name": values_strategy,
        "age": values_strategy,
        "email": values_strategy
    }
)

# keyとvalueの両方を動的に生成するストラテジー
optional_key_strategy = st.dictionaries(
    keys=st.sampled_from(["name", "age", "email"]),
    values=values_strategy,
    min_size=0,  # 最小サイズを0にすることで空の辞書も許容
    max_size=3   # 最大サイズをキーの数と同じに設定
)

# 成功パターンのストラテジー
# expected_key_value_strategy = st.fixed_dictionaries(
#     {
#         "name": st.text(min_size=1),
#         "age": st.integers(min_value=0, max_value=120),
#         "email": st.emails()
#     }
# )

strategy = st.fixed_dictionaries({"profile": random_value_strategy}) | \
           st.fixed_dictionaries({"profile": optional_key_strategy})
        #    st.fixed_dictionaries({"profile": expected_key_value_strategy})


# given() を使ってHypothesisのストラテジをテスト関数に与え、payload引数を使って各テストケースを取得
@settings(verbosity=Verbosity.verbose, max_examples=1000)
@given(strategy)
def test_post(request_payload):
    # テスト実行
    response = test_client.post("/users", json=request_payload)
    # ペイロードがopenapi.jsonの仕様に準拠しているかどうかを判断
    if is_valid_payload(request_payload, create_user_schema):
        assert response.status_code == 201
    else:
        assert response.status_code == 422
