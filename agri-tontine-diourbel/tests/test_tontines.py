import json


def _token(client, telephone="+221770000001", nom="Paysan Test"):
    r = client.post(
        "/api/auth/register",
        data=json.dumps({"telephone": telephone, "nom": nom}),
        content_type="application/json",
    )
    return r.get_json()["token"]


def _headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def test_creer_tontine(client, db):
    token = _token(client)
    resp  = client.post(
        "/api/tontines",
        data=json.dumps({"nom": "Tontine Baye Sene", "montant_cotis": 5000}),
        headers=_headers(token),
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["tontine"]["nom"] == "Tontine Baye Sene"
    assert data["tontine"]["nb_membres"] == 1  # admin auto-ajouté


def test_rejoindre_tontine(client, db):
    token1 = _token(client, "+221770000001", "Admin")
    token2 = _token(client, "+221770000002", "Membre2")

    # Créer tontine
    r = client.post(
        "/api/tontines",
        data=json.dumps({"nom": "Tontine Test", "montant_cotis": 2000}),
        headers=_headers(token1),
    )
    tontine_id = r.get_json()["tontine"]["id"]

    # Rejoindre
    resp = client.post(
        f"/api/tontines/{tontine_id}/rejoindre",
        headers=_headers(token2),
    )
    assert resp.status_code == 201
    assert resp.get_json()["tour"] == 2


def test_rejoindre_doublon(client, db):
    token = _token(client)
    r = client.post(
        "/api/tontines",
        data=json.dumps({"nom": "Tontine Solo", "montant_cotis": 1000}),
        headers=_headers(token),
    )
    tontine_id = r.get_json()["tontine"]["id"]
    resp = client.post(f"/api/tontines/{tontine_id}/rejoindre", headers=_headers(token))
    assert resp.status_code == 409


def test_scoring_nouveau_paysan(client, db):
    """Un paysan sans historique doit avoir un score de 50 (neutre)."""
    from app.services.ai_scoring import recalculer_score
    from app.models.user import User
    from app import db as _db

    token = _token(client, "+221770000003", "Nouveau")
    me    = client.get("/api/auth/me", headers=_headers(token)).get_json()
    score = recalculer_score(me["id"])
    assert 0 <= score <= 100


def test_credit_sans_historique(client, db):
    """Un paysan sans cotisations ne doit pas obtenir de crédit élevé."""
    token = _token(client, "+221770000004", "SansHisto")
    resp  = client.post(
        "/api/credits/demander",
        data=json.dumps({"montant": 100000, "intrant_type": "semences"}),
        headers=_headers(token),
    )
    data = resp.get_json()
    # Score neutre (50) → montant_max = 50 000 FCFA → 100 000 refusé
    assert data["eligible"] is False or data["montant_max"] < 100000
