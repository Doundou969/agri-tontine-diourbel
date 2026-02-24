import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__)

SENEGAL_TEL_RE = re.compile(r"^\+221(70|75|76|77|78)\d{7}$")


def _valider_telephone(tel: str) -> bool:
    return bool(SENEGAL_TEL_RE.match(tel))


@auth_bp.route("/register", methods=["POST"])
def register():
    """Inscription d'un nouveau paysan."""
    data = request.get_json(silent=True) or {}
    tel  = data.get("telephone", "").strip()
    nom  = data.get("nom", "").strip()

    if not tel or not nom:
        return jsonify({"erreur": "telephone et nom sont obligatoires"}), 400

    if not _valider_telephone(tel):
        return jsonify({"erreur": "Numéro invalide. Format: +221XXXXXXXXX (70/75/76/77/78)"}), 400

    if User.query.filter_by(telephone=tel).first():
        return jsonify({"erreur": "Ce numéro est déjà inscrit"}), 409

    paysan = User(
        telephone=tel,
        nom=nom,
        village=data.get("village", ""),
        region=data.get("region", "Diourbel"),
    )
    db.session.add(paysan)
    db.session.commit()

    token = create_access_token(identity=paysan.id)
    return jsonify({
        "message": f"Bienvenue {paysan.nom} !",
        "token":   token,
        "paysan":  paysan.to_dict(),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Connexion par numéro de téléphone."""
    data = request.get_json(silent=True) or {}
    tel  = data.get("telephone", "").strip()

    paysan = User.query.filter_by(telephone=tel, actif=True).first()
    if not paysan:
        return jsonify({"erreur": "Numéro non trouvé ou compte désactivé"}), 404

    token = create_access_token(identity=paysan.id)
    return jsonify({
        "token":  token,
        "paysan": paysan.to_dict(),
    })


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Profil du paysan connecté."""
    paysan = User.query.get_or_404(get_jwt_identity())
    return jsonify(paysan.to_dict())
