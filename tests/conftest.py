import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import ContentType

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def seed_category(db_session):
    category = ContentType(contentTypeId="12", name="관광지")
    db_session.add(category)
    db_session.commit()
    return category


@pytest.fixture
def seed_second_category(db_session):
    category = ContentType(contentTypeId="14", name="문화시설")
    db_session.add(category)
    db_session.commit()
    return category


@pytest.fixture
def create_post(db_session, seed_category):
    from app.models import Post

    post = Post(
        title="First post",
        content="First content",
        password="1234",
        image_path="/images/1.png",
        category_id="12",
        views=3,
        likes=2,
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post