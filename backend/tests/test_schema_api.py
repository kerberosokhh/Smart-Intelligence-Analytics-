def test_schema_api(client) -> None:
    resp = client.get("/api/schema")
    assert resp.status_code == 200
    body = resp.json()
    assert "biz_orders" in body["tables"]
    columns = {c["name"] for c in body["tables"]["biz_orders"]["columns"]}
    assert {"product", "category", "amount", "region", "order_date", "quantity"} <= columns


def test_demo_data_loaded(client) -> None:
    from app.db.sqlite import execute_readonly_query

    rows = execute_readonly_query("SELECT COUNT(*) AS cnt FROM biz_orders")
    assert rows[0]["cnt"] >= 50
