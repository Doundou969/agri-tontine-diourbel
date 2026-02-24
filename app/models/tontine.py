from datetime import datetime
from app import db


class Tontine(db.Model):
    __tablename__ = "tontines"

    id             = db.Column(db.Integer, primary_key=True)
    nom            = db.Column(db.String(100), nullable=False)
    montant_cotis  = db.Column(db.Integer, nullable=False)   # FCFA par tour
    frequence      = db.Column(db.String(20), default="hebdomadaire")  # hebdomadaire | mensuel
    nb_membres_max = db.Column(db.Integer, default=20)
    actif          = db.Column(db.Boolean, default=True)
    admin_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    cree_le        = db.Column(db.DateTime, default=datetime.utcnow)

    admin   = db.relationship("User", foreign_keys=[admin_id])
    membres = db.relationship("Membre", back_populates="tontine", lazy="dynamic",
                              cascade="all, delete-orphan")

    @property
    def nb_membres(self):
        return self.membres.count()

    @property
    def pot_total(self):
        return self.montant_cotis * self.nb_membres

    def to_dict(self):
        return {
            "id":             self.id,
            "nom":            self.nom,
            "montant_cotis":  self.montant_cotis,
            "frequence":      self.frequence,
            "nb_membres_max": self.nb_membres_max,
            "nb_membres":     self.nb_membres,
            "pot_total":      self.pot_total,
            "actif":          self.actif,
            "admin_id":       self.admin_id,
            "cree_le":        self.cree_le.isoformat(),
        }


class Membre(db.Model):
    __tablename__ = "membres"

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"),     nullable=False)
    tontine_id  = db.Column(db.Integer, db.ForeignKey("tontines.id"),  nullable=False)
    tour_numero = db.Column(db.Integer, nullable=True)   # rang dans la rotation
    a_recu_pot  = db.Column(db.Boolean, default=False)
    rejoint_le  = db.Column(db.DateTime, default=datetime.utcnow)

    user    = db.relationship("User",    back_populates="membres")
    tontine = db.relationship("Tontine", back_populates="membres")
    cotisations = db.relationship("Cotisation", back_populates="membre",
                                  lazy="dynamic", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("user_id", "tontine_id", name="uq_user_tontine"),
    )

    def to_dict(self):
        return {
            "id":          self.id,
            "user_id":     self.user_id,
            "nom":         self.user.nom if self.user else "",
            "tontine_id":  self.tontine_id,
            "tour_numero": self.tour_numero,
            "a_recu_pot":  self.a_recu_pot,
            "rejoint_le":  self.rejoint_le.isoformat(),
        }
