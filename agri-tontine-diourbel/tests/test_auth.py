import json


def _register(client, telephone="+221770000001", nom="Baye Test"):
    return client.post(
        "/api/auth/register",
        data=json.dumps({"telephone": telephone, "nom": nom, "village": "Touba Toul"}),
        content_type="application/json",
    )


def test_register_succes(client, db):
    resp = _register(client)
    assert resp.status_code == 201
    data = resp.get_json()
    assert "token" in data
    assert data["paysan"]["telephone"] == "+221770000001"


def test_register_telephone_invalide(client, db):
    resp = _register(client, telephone="0612345678")
    assert resp.status_code == 400
    assert "invalide" in resp.get_json()["erreur"].lower()


def test_register_doublon(client, db):
    _register(client)
    resp = _register(client)   # même numéro
    assert resp.status_code == 409


def test_login_succes(client, db):
    _register(client)
    resp = client.post(
        "/api/auth/login",
        data=json.dumps({"telephone": "+221770000001"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert "token" in resp.get_json()


def test_login_inconnu(client, db):
    resp = client.post(
        "/api/auth/login",
        data=json.dumps({"telephone": "+221770000099"}),
        content_type="application/json",
    )
    assert resp.status_code == 404
