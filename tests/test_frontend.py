from fastapi.testclient import TestClient
from app.main import create_app


def test_frontend_and_auth(tmp_path):
    app = create_app(
        db_path=str(tmp_path / "ui.db"),
        keys={"test-key": {"role": "editor", "user_id": "test", "clients": ["*"]}},
        seed_demo=True,
        run_worker=False,
    )
    with TestClient(app) as client:
        page = client.get("/")
        assert page.status_code == 200
        assert "Карта ЛПР" in page.text
        assert "test-key" not in page.text
        for name in ("styles.css", "app.js", "icons.js"):
            assert client.get("/ui-assets/" + name).status_code == 200
        assert client.get("/api/v1/clients").status_code == 401
        headers = {"X-API-Key": "test-key"}
        clients = client.get("/api/v1/clients", headers=headers).json()["items"]
        assert clients
        result = client.get("/api/v1/clients/" + clients[0]["id"] + "/map", headers=headers)
        assert result.status_code == 200
        assert "nodes" in result.json()
