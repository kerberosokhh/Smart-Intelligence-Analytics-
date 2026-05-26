def test_list_and_create_session(client) -> None:
    empty = client.get("/api/sessions")
    assert empty.status_code == 200
    assert empty.json() == []

    created = client.post("/api/sessions", json={"title": "测试会话"})
    assert created.status_code == 201
    body = created.json()
    assert body["title"] == "测试会话"
    assert "id" in body
    assert "createdAt" in body

    listed = client.get("/api/sessions")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_update_delete_session(client) -> None:
    session_id = client.post("/api/sessions", json={}).json()["id"]

    updated = client.patch(f"/api/sessions/{session_id}", json={"title": "重命名"})
    assert updated.status_code == 200
    assert updated.json()["title"] == "重命名"

    deleted = client.delete(f"/api/sessions/{session_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/api/sessions/{session_id}/messages")
    assert missing.status_code == 404


def test_session_messages_empty(client) -> None:
    session_id = client.post("/api/sessions", json={}).json()["id"]
    resp = client.get(f"/api/sessions/{session_id}/messages")
    assert resp.status_code == 200
    assert resp.json() == []
