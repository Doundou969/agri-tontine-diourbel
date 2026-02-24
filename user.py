from datetime import datetime
from app import db


class User(db.Model):
    __tablename__ = "users"

    id           = db.Column(db.Integer, primary_key=True)
    telephone    = db.Column(db.String(20), unique=True, nullable=False)  # +221XXXXXXXXX
    nom          = db.Column(db.String(100), nullable=False)
    village      = db.Column(db.String(100), default="")
    region       = db.Column(db.String(50), default="Diourbel")
    score_credit = db.Column(db.Float, default=50.0)   # 0 – 100
    actif        = db.Column(db.Boolean, default=True)
    cree_le      = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    membres  = db.relationship("Membre",  back_populates="user",   lazy="dynamic")
    credits  = db.relationship("Credit",  back_populates="paysan", lazy="dynamic")

    def to_dict(self):
        return {
            "id":           self.id,
            "telephone":    self.telephone,
            "nom":          self.nom,
            "village":      self.village,
            "region":       self.region,
            "score_credit": round(self.score_credit, 1),
            "actif":        self.actif,
            "cree_le":      self.cree_le.isoformat(),
        }

    def __repr__(self):
        return f"<User {self.telephone} — {self.nom}>"
