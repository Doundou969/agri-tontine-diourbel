# 🌾 TONTINE+ — Fintech Tontine Agricole · Diourbel, Sénégal

[![CI](https://github.com/VOTRE_USERNAME/agri-tontine-diourbel/actions/workflows/ci.yml/badge.svg)](https://github.com/VOTRE_USERNAME/agri-tontine-diourbel/actions)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com)
[![Licence](https://img.shields.io/badge/Licence-MIT-yellow.svg)](LICENSE)

> **Digitaliser les tontines de village pour financer les intrants agricoles — sans banque, sans garantie, avec un téléphone basique.**

---

## 🎯 Le Problème

Plus de **70% des paysans sénégalais** n'ont pas accès au crédit formel. Pour acheter semences et engrais avant l'hivernage, ils dépendent de tontines informelles (opaque, fraude, zéro traçabilité) ou de prêteurs à **30–50%/mois** — perdant jusqu'à 40% de rendement potentiel.

## 💡 La Solution

**TONTINE+** transforme les tontines traditionnelles en **coopératives financières numériques** :

- ✅ Enregistrement & paiement des cotisations via **Wave** (mobile money)
- ✅ **Scoring IA** sur historique de cotisations → accès microcrédits intrants
- ✅ Partenariats **DER / FADA / PAM CAS** pour débloquer les fonds
- ✅ Mode **SMS hors-ligne** pour les zones sans internet
- ✅ API REST légère — fonctionne sur smartphones bas de gamme

---

## 🗂 Structure du Projet

```
agri-tontine-diourbel/
├── app/
│   ├── models/          # User, Tontine, Membre, Cotisation, Credit
│   ├── routes/          # auth, tontines, cotisations, credits
│   ├── services/        # Wave API, scoring IA
│   └── config.py        # dev / test / prod
├── tests/               # pytest (>70% coverage)
├── .github/workflows/   # CI GitHub Actions
├── run.py               # Point d'entrée
├── requirements.txt
└── .env.example
```

---

## 🚀 Démarrage Rapide

### 1. Cloner & installer

```bash
git clone https://github.com/VOTRE_USERNAME/agri-tontine-diourbel.git
cd agri-tontine-diourbel
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurer l'environnement

```bash
cp .env.example .env
# Éditer .env avec vos clés Wave et Africa's Talking
```

### 3. Lancer l'API

```bash
python run.py
# → API disponible sur http://localhost:5000
```

### 4. Sur Replit

1. Créer un nouveau Repl Python
2. Importer depuis GitHub ou copier les fichiers
3. Dans le Shell : `pip install -r requirements.txt`
4. Configurer les Secrets Replit (équivalent de .env)
5. Cliquer **Run** → votre API tourne immédiatement

---

## 📡 Endpoints API

### Authentification

| Méthode | Route | Description |
|---------|-------|-------------|
| `POST` | `/api/auth/register` | Inscription paysan (+221XXXXXXXXX) |
| `POST` | `/api/auth/login` | Connexion par téléphone |
| `GET`  | `/api/auth/me` | Profil + score crédit |

### Tontines

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET`  | `/api/tontines` | Lister toutes les tontines |
| `POST` | `/api/tontines` | Créer une tontine |
| `GET`  | `/api/tontines/<id>` | Détail + membres |
| `POST` | `/api/tontines/<id>/rejoindre` | Rejoindre |

### Cotisations

| Méthode | Route | Description |
|---------|-------|-------------|
| `POST` | `/api/cotisations/payer` | Payer via Wave + scoring auto |
| `GET`  | `/api/cotisations/historique/<membre_id>` | Historique |
| `GET`  | `/api/cotisations/retards/<tontine_id>` | Membres en retard |

### Crédits

| Méthode | Route | Description |
|---------|-------|-------------|
| `POST` | `/api/credits/demander` | Demande microcrédit intrants |
| `GET`  | `/api/credits/mes-credits` | Mes demandes |
| `POST` | `/api/credits/<id>/rembourser` | Rembourser |

---

## 🧪 Tests

```bash
# Lancer tous les tests
pytest tests/ -v

# Avec couverture
pytest tests/ --cov=app --cov-report=term-missing

# Un fichier spécifique
pytest tests/test_auth.py -v
```

---

## 🤖 Scoring IA

Le score crédit (0–100) est calculé automatiquement après chaque cotisation :

| Critère | Poids |
|---------|-------|
| Taux de paiement des cotisations | 60% |
| Participation multi-tontines | 15% |
| Ancienneté / volume transactions | 10% |
| Crédits remboursés (bonus) | 10% |
| Malus par retard | -5 pts |

**Éligibilité crédit** : score ≥ 40 / plafond = score × 1 000 FCFA

---

## 💰 Modèle Économique

| Source | Mécanisme | Taux |
|--------|-----------|------|
| Commission cotisations | Sur chaque paiement Wave | 1,5% |
| Frais dossier crédit | Par dossier approuvé | 2 000 FCFA |
| Abonnement admin | Par tontine/mois | 1 000 FCFA |
| Partenariat DER/FADA | Commission apport affaires | 2% encours |

---

## 🗺 Feuille de Route

- [x] **Semaine 1** — Modèles DB + auth JWT
- [x] **Semaine 2** — API cotisations + scoring IA
- [ ] **Semaine 3** — Intégration Wave réelle + SMS Africa's Talking
- [ ] **Semaine 4** — Pilote 5 tontines à Diourbel + pitch AYuTe

---

## 🤝 Partenaires Cibles

- **DER / FADA** — Financement microcrédits intrants
- **SONACOS** — Réseau collecte arachide Diourbel
- **PAM CAS** — Achats garantis pour paysans scorés
- **Wave Sénégal** — Paiements mobile money

---

## 📄 Licence

MIT — Voir [LICENSE](LICENSE)

---

*Candidature AYuTe Africa Challenge 2026 · VITAGRO/NOVAGRI · Agropole Diourbel*
