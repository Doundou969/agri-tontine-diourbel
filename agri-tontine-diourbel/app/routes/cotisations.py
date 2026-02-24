from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.cotisation import Cotisation
from app.models.tontine import Membre
from app.services.wave_payment import initier_paiement_wave
from app.services.ai_scoring import recalculer_score

cotisations_bp = Blueprint("cotisations", __name__)


@cotisations_bp.route("/payer", methods=["POST"])
@jwt_required()
def payer_cotisation():
    """Enregistre et initie le paiement d'une cotisation via Wave."""
    user_id = get_jwt_identity()
    data    = request.get_json(silent=True) or {}

    membre_id = data.get("membre_id")
    montant   = data.get("montant")

    if not membre_id or not montant:
        return jsonify({"erreur": "membre_id et montant sont obligatoires"}), 400

    membre = Membre.query.get_or_404(membre_id)

    if membre.user_id != user_id:
        return jsonify({"erreur": "Action non autorisée"}), 403

    # Créer la cotisation en statut en_attente
    cotisation = Cotisation(membre_id=membre_id, montant=int(montant))
    db.session.add(cotisation)
    db.session.flush()

    # Appel Wave (sandbox en développement)
    resultat = initier_paiement_wave(
        montant=int(montant),
        telephone=membre.user.telephone,
        reference=f"TON-{membre.tontine_id}-COT-{cotisation.id}",
    )

    if resultat["succes"]:
        cotisation.marquer_paye(resultat["reference"])
        db.session.commit()
        # Recalcule le score IA du paysan
        nouveau_score = recalculer_score(user_id)
        return jsonify({
            "message":      "Cotisation enregistrée avec succès",
            "reference":    resultat["reference"],
            "nouveau_score": round(nouveau_score, 1),
        })

    db.session.rollback()
    return jsonify({"erreur": "Paiement Wave échoué", "detail": resultat.get("erreur")}), 400


@cotisations_bp.route("/historique/<int:membre_id>", methods=["GET"])
@jwt_required()
def historique_cotisations(membre_id):
    """Historique complet des cotisations d'un membre."""
    membre     = Membre.query.get_or_404(membre_id)
    cotisations = (
        membre.cotisations
        .order_by(Cotisation.cree_le.desc())
        .all()
    )
    return jsonify([c.to_dict() for c in cotisations])


@cotisations_bp.route("/retards/<int:tontine_id>", methods=["GET"])
@jwt_required()
def retards_tontine(tontine_id):
    """Liste des membres en retard pour une tontine (admin uniquement)."""
    from app.models.tontine import Tontine
    user_id = get_jwt_identity()
    tontine = Tontine.query.get_or_404(tontine_id)

    if tontine.admin_id != user_id:
        return jsonify({"erreur": "Réservé à l'admin de la tontine"}), 403

    retards = []
    for membre in tontine.membres:
        nb_retard = membre.cotisations.filter_by(statut="retard").count()
        if nb_retard > 0:
            retards.append({
                **membre.to_dict(),
                "nb_retards": nb_retard,
            })

    return jsonify(retards)
