import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient

os.environ["ENVIRONMENT"] = "test"

from app.main import create_app  # noqa: E402


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    app = create_app()
    with TestClient(app) as c:
        yield c

