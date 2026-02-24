"""
Scoring IA — version MVP (formule pondérée).
V2 : remplacer par RandomForest entraîné sur données réelles.
"""


def calculer_features(paysan_id: int) -> dict:
    """Extrait les features du paysan depuis la DB."""
    from app.models.tontine import Membre
    from app.models.cotisation import Cotisation
    from app.models.credit import Credit

    membres = Membre.query.filter_by(user_id=paysan_id).all()
    if not membres:
        return {
            "taux_paiement":    0.5,
            "nb_tontines":      0,
            "nb_cotisations":   0,
            "nb_retards":       0,
            "credits_rembourses": 0,
        }

    toutes_cotis = []
    for m in membres:
        toutes_cotis.extend(m.cotisations.all())

    nb_payees  = sum(1 for c in toutes_cotis if c.statut == "paye")
    nb_retards = sum(1 for c in toutes_cotis if c.statut == "retard")
    taux       = nb_payees / len(toutes_cotis) if toutes_cotis else 0.5

    credits_ok = Credit.query.filter_by(
        paysan_id=paysan_id, statut="rembourse"
    ).count()

    return {
        "taux_paiement":      taux,
        "nb_tontines":        len(membres),
        "nb_cotisations":     len(toutes_cotis),
        "nb_retards":         nb_retards,
        "credits_rembourses": credits_ok,
    }


def calculer_score(features: dict) -> float:
    """
    Formule pondérée MVP (score 0–100).

    Poids :
      60% → taux de paiement des cotisations (fiabilité)
      15% → participation multi-tontines (engagement)
      10% → volume de transactions (ancienneté)
      10% → bonus crédits remboursés
      -5  → malus par retard
    """
    score = (
        features["taux_paiement"]                    * 60
        + min(features["nb_tontines"]    / 5,  1.0)  * 15
        + min(features["nb_cotisations"] / 24, 1.0)  * 10
        + min(features["credits_rembourses"] / 3, 1.0) * 10
        - features["nb_retards"]                     * 5
    )
    return max(0.0, min(100.0, score))


def recalculer_score(paysan_id: int) -> float:
    """Recalcule et persiste le score crédit du paysan."""
    from app import db
    from app.models.user import User

    features = calculer_features(paysan_id)
    score    = calculer_score(features)

    paysan = User.query.get(paysan_id)
    if paysan:
        paysan.score_credit = score
        db.session.commit()

    return score


def est_eligible_credit(paysan_id: int, montant_demande: int) -> dict:
    """
    Vérifie l'éligibilité à un microcrédit.

    Règles MVP :
      - Score minimum : 40 / 100
      - Montant max   : score × 1 000 FCFA  (ex: score 70 → 70 000 FCFA)
    """
    score       = recalculer_score(paysan_id)
    montant_max = int(score * 1_000)

    if score < 40:
        raison = f"Score insuffisant ({score:.1f}/100). Minimum requis : 40."
    elif montant_demande > montant_max:
        raison = (
            f"Montant demandé ({montant_demande:,} FCFA) dépasse "
            f"votre plafond ({montant_max:,} FCFA)."
        )
    else:
        raison = "Éligible."

    return {
        "eligible":   score >= 40 and montant_demande <= montant_max,
        "score":      score,
        "montant_max": montant_max,
        "raison":     raison,
    }
