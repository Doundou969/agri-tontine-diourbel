from datetime import datetime, date
from app import db


class Credit(db.Model):
    __tablename__ = "credits"

    id              = db.Column(db.Integer, primary_key=True)
    paysan_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    montant         = db.Column(db.Integer, nullable=False)   # FCFA
    intrant_type    = db.Column(db.String(50), default="mixte")
    # intrant_type: semences | engrais | pesticides | mixte
    statut          = db.Column(db.String(20), default="demande")
    # statut: demande | approuve | refuse | rembourse
    score_snapshot  = db.Column(db.Float)       # score IA au moment de la demande
    montant_max_autorise = db.Column(db.Integer)
    echeance        = db.Column(db.Date, nullable=True)
    partenaire      = db.Column(db.String(50), default="DER")  # DER | FADA | PAM
    note_agent      = db.Column(db.Text, nullable=True)
    cree_le         = db.Column(db.DateTime, default=datetime.utcnow)
    mis_a_jour_le   = db.Column(db.DateTime, default=datetime.utcnow,
                                onupdate=datetime.utcnow)

    paysan = db.relationship("User", back_populates="credits")

    def to_dict(self):
        return {
            "id":                   self.id,
            "paysan_id":            self.paysan_id,
            "nom_paysan":           self.paysan.nom if self.paysan else "",
            "montant":              self.montant,
            "intrant_type":         self.intrant_type,
            "statut":               self.statut,
            "score_snapshot":       self.score_snapshot,
            "montant_max_autorise": self.montant_max_autorise,
            "echeance":             self.echeance.isoformat() if self.echeance else None,
            "partenaire":           self.partenaire,
            "cree_le":              self.cree_le.isoformat(),
        }
