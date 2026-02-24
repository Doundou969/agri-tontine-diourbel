"""
Service d'intégration Wave Sénégal.
En développement : mode sandbox (pas de vrai paiement).
En production    : remplacer WAVE_SANDBOX=False dans .env
"""
import os
import uuid
import requests
from flask import current_app


WAVE_SANDBOX = os.environ.get("WAVE_SANDBOX", "true").lower() == "true"


def initier_paiement_wave(montant: int, telephone: str, reference: str) -> dict:
    """
    Initie un paiement Wave.
    Retourne: {"succes": bool, "reference": str, "erreur": str|None}
    """
    if WAVE_SANDBOX:
        return _sandbox_paiement(montant, telephone, reference)

    return _wave_api_paiement(montant, telephone, reference)


def _sandbox_paiement(montant: int, telephone: str, reference: str) -> dict:
    """Simule un paiement réussi en mode sandbox."""
    fake_ref = f"WAVE-SANDBOX-{uuid.uuid4().hex[:12].upper()}"
    current_app.logger.info(
        f"[SANDBOX] Paiement simulé | {montant} FCFA | {telephone} | ref={fake_ref}"
    )
    return {"succes": True, "reference": fake_ref, "erreur": None}


def _wave_api_paiement(montant: int, telephone: str, reference: str) -> dict:
    """Appel réel à l'API Wave (production)."""
    api_key  = current_app.config.get("WAVE_API_KEY")
    base_url = current_app.config.get("WAVE_BASE_URL", "https://api.wave.com/v1")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type":  "application/json",
    }
    payload = {
        "currency":   "XOF",
        "amount":     str(montant),
        "error_url":  "https://agri-tontine-diourbel.com/erreur",
        "success_url":"https://agri-tontine-diourbel.com/succes",
        "client_reference": reference,
    }

    try:
        resp = requests.post(f"{base_url}/checkout/sessions", json=payload,
                             headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            "succes":    True,
            "reference": data.get("id", reference),
            "erreur":    None,
        }
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Wave API erreur: {e}")
        return {"succes": False, "reference": None, "erreur": str(e)}
