from datetime import date, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.credit import Credit
from app.services.ai_scoring import est_eligible_credit

credits_bp = Blueprint("credits", __name__)

PARTENAIRES_VALIDES = {"DER", "FADA", "PAM"}
INTRANTS_VALIDES    = {"semences", "engrais", "pesticides", "mixte"}


@credits_bp.route("/demander", methods=["POST"])
@jwt_required()
def demander_credit():
    """Déposer une demande de microcrédit intrants."""
    paysan_id = get_jwt_identity()
    data      = request.get_json(silent=True) or {}

    montant      = data.get("montant")
    intrant_type = data.get("intrant_type", "mixte")
    partenaire   = data.get("partenaire", "DER")

    if not montant or int(montant) < 5000:
        return jsonify({"erreur": "Montant minimum : 5 000 FCFA"}), 400

    if intrant_type not in INTRANTS_VALIDES:
        return jsonify({"erreur": f"intrant_type: {', '.join(INTRANTS_VALIDES)}"}), 400

    if partenaire not in PARTENAIRES_VALIDES:
        return jsonify({"erreur": f"partenaire: {', '.join(PARTENAIRES_VALIDES)}"}), 400

    # Vérification éligibilité IA
    eligibilite = est_eligible_credit(paysan_id, int(montant))

    credit = Credit(
        paysan_id      = paysan_id,
        montant        = int(montant),
        intrant_type   = intrant_type,
        partenaire     = partenaire,
        score_snapshot = eligibilite["score"],
        montant_max_autorise = eligibilite["montant_max"],
        statut         = "approuve" if eligibilite["eligible"] else "refuse",
        echeance       = date.today() + timedelta(days=180),  # 6 mois
    )
    db.session.add(credit)
    db.session.commit()

    status_code = 201 if eligibilite["eligible"] else 200
    return jsonify({
        "eligible":   eligibilite["eligible"],
        "statut":     credit.statut,
        "score":      round(eligibilite["score"], 1),
        "montant_max": eligibilite["montant_max"],
        "raison":     eligibilite["raison"],
        "credit":     credit.to_dict(),
    }), status_code


@credits_bp.route("/mes-credits", methods=["GET"])
@jwt_required()
def mes_credits():
    """Liste des demandes de crédit du paysan connecté."""
    paysan_id = get_jwt_identity()
    credits = (
        Credit.query
        .filter_by(paysan_id=paysan_id)
        .order_by(Credit.cree_le.desc())
        .all()
    )
    return jsonify([c.to_dict() for c in credits])


@credits_bp.route("/<int:credit_id>/rembourser", methods=["POST"])
@jwt_required()
def rembourser_credit(credit_id):
    """Marquer un crédit comme remboursé."""
    paysan_id = get_jwt_identity()
    credit    = Credit.query.get_or_404(credit_id)

    if credit.paysan_id != paysan_id:
        return jsonify({"erreur": "Action non autorisée"}), 403

    if credit.statut != "approuve":
        return jsonify({"erreur": "Seuls les crédits approuvés peuvent être remboursés"}), 400

    credit.statut = "rembourse"
    db.session.commit()

    # Bonus score après remboursement
    from app.services.ai_scoring import recalculer_score
    nouveau_score = recalculer_score(paysan_id)

    return jsonify({
        "message":      "Crédit remboursé. Merci !",
        "nouveau_score": round(nouveau_score, 1),
    })
