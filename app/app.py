from typing import Union
from fastapi import FastAPI

app = FastAPI(debug=True, docs_url="/docs/users")

from api import api
