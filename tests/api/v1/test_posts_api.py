from datetime import datetime, UTC
from fastapi.testclient import TestClient

from app.models import Post


def test_get_recent_posts_empty(client, seed_category):
    response = client.get("/api/v1/posts/recent")

    assert response.status_code == 200
    assert response.json() == []


def test_create_post_success(client, seed_category):
    payload = {
        "title": "Hello",
        "content": "World",
        "password": "1234",
        "image_path": "/images/hello.png",
        "category_name": "관광지",
    }

    response = client.post("/api/v1/posts", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Hello"
    assert data["content"] == "World"
    assert data["image_path"] == "/images/hello.png"
    assert data["views"] == 0
    assert data["likes"] == 0
    assert data["category_name"] == "관광지"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_post_category_not_found(client):
    payload = {
        "title": "Hello",
        "content": "World",
        "password": "1234",
        "image_path": None,
        "category_name": "존재하지 않는 카테고리",
    }

    response = client.post("/api/v1/posts", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}


def test_get_posts_list(client, db_session, seed_category, seed_second_category):
    posts = [
        Post(
            title="Alpha",
            content="Alpha content",
            password="1111",
            category_id="12",
            views=10,
            likes=1,
            created_at=datetime(2024, 1, 1, tzinfo=UTC),
            updated_at=datetime(2024, 1, 1, tzinfo=UTC),
        ),
        Post(
            title="Beta",
            content="Beta content",
            password="2222",
            category_id="14",
            views=20,
            likes=5,
            created_at=datetime(2024, 1, 2, tzinfo=UTC),
            updated_at=datetime(2024, 1, 2, tzinfo=UTC),
        ),
        Post(
            title="Gamma keyword",
            content="Contains search term",
            password="3333",
            category_id="12",
            views=30,
            likes=9,
            created_at=datetime(2024, 1, 3, tzinfo=UTC),
            updated_at=datetime(2024, 1, 3, tzinfo=UTC),
        ),
    ]
    db_session.add_all(posts)
    db_session.commit()

    response = client.get("/api/v1/posts?page=1&page_size=2&sort_by=created_at&sort_order=desc")

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total"] == 3
    assert data["total_pages"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["title"] == "Gamma keyword"
    assert data["items"][1]["title"] == "Beta"


def test_get_posts_keyword_filter(client, db_session, seed_category):
    db_session.add_all(
        [
            Post(
                title="Search target",
                content="No match here",
                password="1111",
                category_id="12",
            ),
            Post(
                title="Other title",
                content="Keyword appears in content",
                password="2222",
                category_id="12",
            ),
            Post(
                title="Unrelated",
                content="Nothing useful",
                password="3333",
                category_id="12",
            ),
        ]
    )
    db_session.commit()

    response = client.get("/api/v1/posts?keyword=Keyword")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Other title"


def test_get_post_detail(client, create_post):
    response = client.get(f"/api/v1/posts/{create_post.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == create_post.id
    assert data["title"] == "First post"
    assert data["category_name"] == "관광지"


def test_get_post_not_found(client):
    response = client.get("/api/v1/posts/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Post not found"}


def test_verify_post_password_true(client, create_post):
    response = client.post(
        f"/api/v1/posts/{create_post.id}/verify",
        json={"password": "1234"},
    )

    assert response.status_code == 200


def test_verify_post_password_false(client, create_post):
    response = client.post(
        f"/api/v1/posts/{create_post.id}/verify",
        json={"password": "wrong"},
    )

    assert response.status_code == 401


def test_update_post_success(client, create_post, seed_second_category):
    payload = {
        "title": "Updated title",
        "content": "Updated content",
        "image_path": "/images/updated.png",
        "category_name": "문화시설",
    }

    response = client.put(f"/api/v1/posts/{create_post.id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated title"
    assert data["content"] == "Updated content"
    assert data["image_path"] == "/images/updated.png"
    assert data["category_name"] == "문화시설"


def test_update_post_category_not_found(client, create_post):
    response = client.put(
        f"/api/v1/posts/{create_post.id}",
        json={
            "category_name": "존재하지 않는 카테고리",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}


def test_delete_post_success(client: TestClient, create_post):
    response = client.delete(
        f"/api/v1/posts/{create_post.id}",
    )

    assert response.status_code == 204
    assert response.content == b""
