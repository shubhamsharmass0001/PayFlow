import os
import sys
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.core.rate_limit import get_redis_client
import app.core.rate_limit as rate_limit_module
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.modules.rbac.seed import seed_rbac_data

from app.core.celery_app import celery_app
celery_app.conf.update(
    task_always_eager=True,
    task_eager_propagates=True,
    broker_url="memory://",
    result_backend="cache+memory://",
)

# Use test postgres instance
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres@127.0.0.1:5433/payflow_test",
)
settings.POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5433"))
settings.POSTGRES_DB = os.getenv("POSTGRES_DB", "payflow_test")

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

import app.db.session as db_session_module
db_session_module.SessionLocal = TestingSessionLocal
db_session_module.engine = engine


class InMemoryRedisPipeline:
    def __init__(self, store: dict, ttls: dict):
        self.store = store
        self.ttls = ttls
        self.commands = []

    def incr(self, key: str):
        self.commands.append(("incr", key))
        return self

    def ttl(self, key: str):
        self.commands.append(("ttl", key))
        return self

    def execute(self):
        results = []
        for cmd, key in self.commands:
            if cmd == "incr":
                val = self.store.get(key, 0) + 1
                self.store[key] = val
                results.append(val)
            elif cmd == "ttl":
                results.append(self.ttls.get(key, 900))
        self.commands.clear()
        return results


class InMemoryRedis:
    def __init__(self):
        self.store = {}
        self.ttls = {}

    def pipeline(self):
        return InMemoryRedisPipeline(self.store, self.ttls)

    def expire(self, key: str, seconds: int):
        self.ttls[key] = seconds
        return True

    def get(self, key: str):
        return self.store.get(key)

    def set(self, key: str, value: any, nx: bool = False, ex: int = None, px: int = None):
        if nx and key in self.store:
            return False
        self.store[key] = str(value)
        if ex:
            self.ttls[key] = ex
        return True

    def setnx(self, key: str, value: any) -> int:
        if key in self.store:
            return 0
        self.store[key] = str(value)
        return 1

    def delete(self, *keys):
        count = 0
        for k in keys:
            if k in self.store:
                del self.store[k]
                self.ttls.pop(k, None)
                count += 1
        return count

    def keys(self, pattern: str = "*"):
        import fnmatch
        return [k for k in self.store.keys() if fnmatch.fnmatch(k, pattern)]

    def scan_iter(self, match: str = "*"):
        for k in self.keys(match):
            yield k

    def flushall(self):
        self.store.clear()
        self.ttls.clear()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    # Keep schema intact or cleanup


@pytest.fixture
def db() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def fake_redis(monkeypatch) -> InMemoryRedis:
    redis_instance = InMemoryRedis()
    monkeypatch.setattr(rate_limit_module, "get_redis_client", lambda: redis_instance)
    return redis_instance


@pytest.fixture
def client(db: Session, fake_redis) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
