import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.base import Base
from app.main import app


@pytest.mark.asyncio
async def test_register_login_me_flow() -> None:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # register
            r = await client.post(
                "/auth/register",
                json={"email": "integration@example.com", "password": "StrongPass123!"},
            )
            assert r.status_code == 200, r.text

            # login (OAuth2 form-data)
            r = await client.post(
                "/auth/login",
                data={
                    "username": "integration@example.com",
                    "password": "StrongPass123!",
                },
            )
            assert r.status_code == 200, r.text
            token = r.json()["access_token"]

            # me
            r = await client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert r.status_code == 200, r.text
            body = r.json()
            assert body["email"] == "integration@example.com"
            assert body["role"] == "user"
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.mark.asyncio
async def test_auth_negative_cases() -> None:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # initial register
            r = await client.post(
                "/auth/register",
                json={"email": "dup@example.com", "password": "StrongPass123!"},
            )
            assert r.status_code == 200, r.text

            # duplicate register -> 409
            r = await client.post(
                "/auth/register",
                json={"email": "dup@example.com", "password": "StrongPass123!"},
            )
            assert r.status_code == 409, r.text

            # wrong password -> 401
            r = await client.post(
                "/auth/login",
                data={"username": "dup@example.com", "password": "wrong-pass"},
            )
            assert r.status_code == 401, r.text

            # /me without token -> 401
            r = await client.get("/auth/me")
            assert r.status_code == 401, r.text

            # /me with invalid token -> 401
            r = await client.get(
                "/auth/me",
                headers={"Authorization": "Bearer definitely-invalid-token"},
            )
            assert r.status_code == 401, r.text
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()
