from datetime import datetime
from app import db


class Cotisation(db.Model):
    __tablename__ = "cotisations"

    id            = db.Column(db.Integer, primary_key=True)
    membre_id     = db.Column(db.Integer, db.ForeignKey("membres.id"), nullable=False)
    montant       = db.Column(db.Integer, nullable=False)  # FCFA
    statut        = db.Column(db.String(20), default="en_attente")
    # statut: en_attente | paye | retard | partiel
    wave_ref      = db.Column(db.String(100), nullable=True)
    date_paiement = db.Column(db.DateTime, nullable=True)
    cree_le       = db.Column(db.DateTime, default=datetime.utcnow)

    membre = db.relationship("Membre", back_populates="cotisations")

    def marquer_paye(self, wave_ref: str):
        self.statut        = "paye"
        self.wave_ref      = wave_ref
        self.date_paiement = datetime.utcnow()

    def to_dict(self):
        return {
            "id":            self.id,
            "membre_id":     self.membre_id,
            "montant":       self.montant,
            "statut":        self.statut,
            "wave_ref":      self.wave_ref,
            "date_paiement": self.date_paiement.isoformat() if self.date_paiement else None,
            "cree_le":       self.cree_le.isoformat(),
        }
