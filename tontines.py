from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.tontine import Tontine, Membre
from app.models.user import User

tontines_bp = Blueprint("tontines", __name__)


@tontines_bp.route("", methods=["GET"])
@jwt_required()
def lister_tontines():
    """Liste toutes les tontines actives."""
    tontines = Tontine.query.filter_by(actif=True).order_by(Tontine.cree_le.desc()).all()
    return jsonify([t.to_dict() for t in tontines])


@tontines_bp.route("", methods=["POST"])
@jwt_required()
def creer_tontine():
    """Créer une nouvelle tontine."""
    data     = request.get_json(silent=True) or {}
    admin_id = get_jwt_identity()

    nom           = data.get("nom", "").strip()
    montant_cotis = data.get("montant_cotis")
    frequence     = data.get("frequence", "hebdomadaire")

    if not nom or not montant_cotis:
        return jsonify({"erreur": "nom et montant_cotis sont obligatoires"}), 400

    if montant_cotis < 500:
        return jsonify({"erreur": "Montant minimum : 500 FCFA"}), 400

    if frequence not in ("hebdomadaire", "mensuel"):
        return jsonify({"erreur": "frequence: hebdomadaire ou mensuel"}), 400

    tontine = Tontine(
        nom=nom,
        montant_cotis=int(montant_cotis),
        frequence=frequence,
        nb_membres_max=data.get("nb_membres_max", 20),
        admin_id=admin_id,
    )
    db.session.add(tontine)
    db.session.flush()  # pour obtenir l'id

    # L'admin est automatiquement le premier membre (tour 1)
    membre = Membre(user_id=admin_id, tontine_id=tontine.id, tour_numero=1)
    db.session.add(membre)
    db.session.commit()

    return jsonify({"message": "Tontine créée", "tontine": tontine.to_dict()}), 201


@tontines_bp.route("/<int:tontine_id>", methods=["GET"])
@jwt_required()
def detail_tontine(tontine_id):
    """Détail d'une tontine avec ses membres."""
    tontine = Tontine.query.get_or_404(tontine_id)
    data    = tontine.to_dict()
    data["membres"] = [m.to_dict() for m in tontine.membres]
    return jsonify(data)


@tontines_bp.route("/<int:tontine_id>/rejoindre", methods=["POST"])
@jwt_required()
def rejoindre_tontine(tontine_id):
    """Rejoindre une tontine existante."""
    user_id = get_jwt_identity()
    tontine = Tontine.query.get_or_404(tontine_id)

    if not tontine.actif:
        return jsonify({"erreur": "Cette tontine est fermée"}), 400

    if tontine.nb_membres >= tontine.nb_membres_max:
        return jsonify({"erreur": "Tontine complète"}), 400

    if Membre.query.filter_by(user_id=user_id, tontine_id=tontine_id).first():
        return jsonify({"erreur": "Vous êtes déjà membre"}), 409

    prochain_tour = tontine.nb_membres + 1
    membre = Membre(user_id=user_id, tontine_id=tontine_id, tour_numero=prochain_tour)
    db.session.add(membre)
    db.session.commit()

    return jsonify({"message": "Vous avez rejoint la tontine", "tour": prochain_tour}), 201


@tontines_bp.route("/<int:tontine_id>", methods=["DELETE"])
@jwt_required()
def fermer_tontine(tontine_id):
    """Fermer une tontine (admin uniquement)."""
    user_id = get_jwt_identity()
    tontine = Tontine.query.get_or_404(tontine_id)

    if tontine.admin_id != user_id:
        return jsonify({"erreur": "Seul l'admin peut fermer la tontine"}), 403

    tontine.actif = False
    db.session.commit()
    return jsonify({"message": "Tontine fermée"})
