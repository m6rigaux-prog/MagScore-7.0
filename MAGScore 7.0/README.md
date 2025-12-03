# MAGScore 7.0 — Cognitive Edition

> **Vision : NO CHANCE — ONLY PATTERNS**

Bienvenue dans MAGScore 7.0, un moteur d'analyse comportementale neutre pour le football.  
Ce document vous guidera pas à pas, même si vous débutez en Python.

---

## 🎯 Philosophie

MAGScore repose sur un principe fondamental : **l'observation pure, sans prédiction**.

### Ce que MAGScore fait :
- Observer les comportements sur le terrain
- Structurer les données en patterns cohérents
- Produire des rapports neutres et factuels

### Ce que MAGScore ne fait JAMAIS :
- Prédire le résultat d'un match
- Utiliser ou afficher des cotes de paris
- Recommander des mises ou des stratégies de jeu
- Stocker les scores ou résultats finaux

Le slogan "**No Chance – Only Patterns**" résume cette philosophie : MAGScore ne croit pas au hasard, il identifie des schémas comportementaux reproductibles.

---

## 🏗️ Architecture générale

MAGScore 7.0 est composé de plusieurs moteurs qui s'enchaînent dans un pipeline. Voici une présentation simple de chaque composant :

### 1. Vision Engine v1
Extrait des signaux visuels à partir de flux vidéo (si disponible).  
**Signaux détectés** : pression haute, densité de joueurs, désorganisation spatiale.

### 2. Modules de signaux
Analysent les données statistiques du match :
- **Stabilité** : solidité défensive, compacité
- **Intensité** : pressing, duels, courses
- **Psychologie** : frustration, résilience
- **Cohésion** : coordination collective

### 3. Signal Memory Engine v2
Lisse les signaux pour éviter les faux positifs et stabiliser les mesures.

### 4. Behavior Engine v3
Génère les comportements (STB, INT, PSY) en appliquant des règles strictes :
- Minimum **2 signaux convergents** pour activer un comportement
- **3 signaux = pondération × 1.5**
- Priorité aux signaux récents (recency)

### 5. Pattern Engine v2
Combine les comportements en patterns narratifs :
- **Patterns doubles** : 2 comportements liés (ex: STB_01 + PSY_01)
- **Patterns triples** : 3 comportements (ex: STB_01 + PSY_01 + INT_02)
- **Patterns visuels** : combinaisons avec signaux vidéo (ex: STB_01 + VIS_PRESS_HIGH)

### 6. Match Flow Engine v2
Découpe le match en phases chronologiques :
- Phases globales (fond de match)
- Phases finales (dernières 15 minutes)
- Détection de ruptures (changements brutaux)

### 7. Memory Engine v1
Stocke les patterns passés pour enrichir l'analyse :
- **Mémoire épisodique** : 10 derniers matchs de chaque équipe
- **Mémoire sémantique** : fréquences de patterns agrégées

⚠️ **Sécurité** : ce moteur n'accepte JAMAIS les scores, résultats ou cotes.

### 8. Narrative Engine v2 / Analysis Bot v3.2
Produit un rapport structuré en 7 sections :
1. Contexte du match
2. Indicateurs structurels
3. Lecture comportementale
4. Patterns narratifs (+ contexte historique)
5. Match Flow
6. Points clés à retenir
7. Synthèse neutre + disclaimer

### 9. Lexicon Guard v3 & Quality Control Engine v2
- **Lexicon Guard** : filtre les mots interdits (paris, prédictions, etc.)
- **Quality Control** : vérifie la cohérence globale du rapport

---

## 🔄 Enchaînement du Pipeline v2.7

```
Données brutes
       ↓
┌──────────────────────┐
│  normalize_api()     │  ← Normalisation des données
└──────────────────────┘
       ↓
┌──────────────────────┐
│  Modules de signaux  │  ← Stabilité, Intensité, Psychologie, Cohésion
└──────────────────────┘
       ↓
┌──────────────────────┐
│  Signal Memory       │  ← Lissage des signaux
└──────────────────────┘
       ↓
┌──────────────────────┐
│  Vision Engine       │  ← Extraction signaux visuels (si vidéo dispo)
└──────────────────────┘
       ↓
┌──────────────────────┐
│  Behavior Engine     │  ← Génération des comportements
└──────────────────────┘
       ↓
┌──────────────────────┐
│  Pattern Engine v2   │  ← Détection des patterns (+ visuels)
└──────────────────────┘
       ↓
┌──────────────────────┐
│  Match Flow Engine   │  ← Reconstruction chronologique
└──────────────────────┘
       ↓
┌──────────────────────┐
│  Memory Engine       │  ← Stockage sécurisé + contexte historique
└──────────────────────┘
       ↓
┌──────────────────────┐
│  Analysis Bot v3.2   │  ← Génération du rapport
└──────────────────────┘
       ↓
┌──────────────────────┐
│  Lexicon Guard       │  ← Filtrage vocabulaire interdit
└──────────────────────┘
       ↓
┌──────────────────────┐
│  Quality Control     │  ← Vérification cohérence
└──────────────────────┘
       ↓
    Rapport final
```

---

## 🔧 Comportements Officiels

| Code   | Nom                      | Catégorie   | Zone prioritaire |
|--------|--------------------------|-------------|------------------|
| STB_01 | Effondrement Structurel  | Stabilité   | last_15_min      |
| STB_02 | Verrouillage Tactique    | Stabilité   | global           |
| INT_01 | Surge de Pressing        | Intensité   | global           |
| INT_02 | Déclin Physique          | Intensité   | last_15_min      |
| PSY_01 | Frustration Active       | Psychologie | last_15_min      |
| PSY_02 | Résilience               | Psychologie | last_15_min      |

### Patterns visuels (nouveauté 7.0)

| Code       | Nom                          | Sources                    |
|------------|------------------------------|----------------------------|
| PTN_VIS_01 | Défense sous siège visuel    | STB_01 + VIS_PRESS_HIGH    |
| PTN_VIS_02 | Pressing concentré           | INT_01 + VIS_CLUSTER_HIGH  |
| PTN_VIS_03 | Désorganisation spatiale     | STB_01 + VIS_CLUSTER_LOW   |
| PTN_VIS_04 | Contrôle visuel de l'espace  | STB_02 + VIS_PRESS_LOW     |

---

## ⚙️ Configuration de l'environnement

### Étape 1 : Créer un environnement virtuel

Un environnement virtuel isole les dépendances de MAGScore du reste de votre système.

```bash
# Créer l'environnement
python -m venv venv
```

### Étape 2 : Activer l'environnement

**Sous Windows (PowerShell)** :
```powershell
.\venv\Scripts\Activate.ps1
```

**Sous Windows (CMD)** :
```cmd
.\venv\Scripts\activate.bat
```

**Sous Linux/Mac** :
```bash
source venv/bin/activate
```

Vous verrez `(venv)` apparaître devant votre invite de commande.

### Étape 3 : Installer les dépendances

Si un fichier `requirements.txt` est présent :
```bash
pip install -r requirements.txt
```

Sinon, installez les dépendances minimales :
```bash
pip install pytest numpy
```

Pour le Vision Engine (optionnel) :
```bash
pip install opencv-python
```

---

## 📝 Configuration du fichier .env

Créez un fichier `.env` à la racine du projet pour stocker vos paramètres sensibles.

### Exemple de contenu :

```env
# === API Football ===
API_FOOTBALL_KEY=votre_clé_api_ici

# === Vision Engine (optionnel) ===
VIDEO_STREAM_URL=rtsp://votre-flux-video.com/stream
# Flux de démonstration si vous n'avez pas de flux :
# VIDEO_STREAM_URL=rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov

# === Base de données (optionnel) ===
DB_URI=sqlite:///magscore.db

# === Memory Engine ===
MEMORY_MAX_EPISODES=10
MEMORY_RETENTION_DAYS=30

# === Paramètres généraux ===
DEBUG_MODE=false
LOG_LEVEL=INFO
```

### Variables importantes :

| Variable           | Description                                      | Obligatoire |
|--------------------|--------------------------------------------------|-------------|
| API_FOOTBALL_KEY   | Clé d'accès à l'API de données football          | Oui         |
| VIDEO_STREAM_URL   | URL du flux vidéo (HLS, RTSP, MP4)               | Non         |
| DB_URI             | URI de connexion à la base de données            | Non         |
| MEMORY_MAX_EPISODES| Nombre maximum d'épisodes en mémoire (défaut: 10)| Non         |

---

## 🚫 Configuration du fichier .gitignore

Le fichier `.gitignore` empêche certains fichiers d'être versionnés (envoyés sur Git).

### Contenu recommandé :

```gitignore
# === Environnement ===
.env
venv/
.venv/

# === Python ===
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# === Pytest ===
.pytest_cache/
.coverage
htmlcov/

# === IDE ===
.vscode/
.idea/
*.swp

# === MAGScore spécifique ===
logs/
frames/
*.log
magscore.db
output/

# === Données sensibles ===
match_data_*.json
reports/
```

**Important** : Ne versionnez JAMAIS votre fichier `.env` car il contient des clés secrètes.

---

## 🧪 Exécution des tests

Pour vérifier que tout fonctionne correctement, lancez la suite de tests :

```bash
python -m pytest -q
```

### Résultat attendu :
```
317 passed, 4 skipped
```

- **317 passed** : tous les tests fonctionnels réussissent
- **4 skipped** : tests legacy intentionnellement ignorés

### Conseils :

- Relancez les tests après **chaque modification** du code
- Si des tests échouent, lisez attentivement le message d'erreur
- Un test qui échoue indique souvent une régression involontaire

Pour plus de détails sur les tests :
```bash
python -m pytest -v  # Mode verbeux
python -m pytest tests/test_magscore_7_0.py  # Tests spécifiques 7.0
```

---

## 🚀 Lancement d'une analyse

### Exemple basique :

```bash
python -m magscore.orchestration.pipeline --input match_data.json
```

### Avec flux vidéo :

Si `VIDEO_STREAM_URL` est configuré dans votre `.env`, le Vision Engine sera automatiquement activé et enrichira l'analyse avec des signaux visuels.

### Exemple de code Python :

```python
from magscore.orchestration.pipeline import Pipeline

# Créer le pipeline
pipeline = Pipeline(enable_vision=True, enable_memory=True)

# Données du match
raw_data = {
    "stats": {
        "shots": 15,
        "possession": 55,
        "fouls": 12,
        # ... autres statistiques
    },
    "last_15_min": {
        "shots": 4,
        "fouls": 5,
        # ... statistiques des 15 dernières minutes
    }
}

# Métadonnées
metadata = {
    "home_team": "Équipe A",
    "away_team": "Équipe B",
    "competition": "Ligue 1",
}

# Lancer l'analyse
result = pipeline.run_analysis(
    raw_data, 
    metadata,
    team_id="EQUIPE_A"  # Pour la mémoire
)

# Afficher le rapport
print(result["report"])
```

---

## ⚠️ Précautions et bonnes pratiques

### 1. Respecter la neutralité

MAGScore est conçu pour être **100% neutre**. Ne modifiez jamais le code pour :
- Stocker ou afficher des scores
- Calculer des probabilités de victoire
- Intégrer des données de paris ou de cotes

### 2. Gérer les données temporaires

Pour éviter la saturation du disque :
- **Frames vidéo** : purgez régulièrement le dossier `frames/`
- **Mémoire épisodique** : le Memory Engine limite automatiquement à 10 épisodes
- **Logs** : configurez une rotation des logs

```bash
# Nettoyer les données temporaires
rm -rf frames/
rm -rf __pycache__/
```

### 3. Lexique interdit

Le Lexicon Guard bloque automatiquement ces termes dans les rapports :

❌ **Interdits** : favori, probabilité, value, pari, cote, bookmaker, prono, prediction

✅ **Autorisés** : stabilité, intensité, cohésion, dynamique, contrôle, pression

---

## 👶 Pour les débutants en Python

### C'est normal de rencontrer des erreurs !

Quand Python affiche une erreur, ne paniquez pas. Voici comment la lire :

1. **Regardez la dernière ligne** : elle indique le type d'erreur
2. **Remontez le traceback** : chaque ligne `File "..."` indique où le problème s'est produit
3. **Cherchez le message** : copiez-le dans un moteur de recherche

### Erreurs courantes :

| Erreur                        | Cause probable                           | Solution                          |
|-------------------------------|------------------------------------------|-----------------------------------|
| `ModuleNotFoundError`         | Dépendance non installée                 | `pip install <module>`            |
| `FileNotFoundError`           | Fichier ou chemin incorrect              | Vérifiez le chemin                |
| `KeyError`                    | Clé manquante dans un dictionnaire       | Vérifiez les données d'entrée     |
| `ImportError`                 | Environnement virtuel non activé         | Activez le venv                   |

### Ressources utiles :

- [Documentation officielle Python](https://docs.python.org/fr/3/)
- [Tutoriel Real Python](https://realpython.com/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/python)

---

## 📋 Résumé des versions

| Composant          | Version | Nouveautés principales                     |
|--------------------|---------|--------------------------------------------|
| Pipeline           | v2.7    | Intégration Vision + Memory                |
| Pattern Engine     | v2.0    | Patterns visuels, quadruples               |
| Behavior Engine    | v3.0    | Règles recency améliorées                  |
| Match Flow Engine  | v1.1    | Détection de ruptures                      |
| Memory Engine      | v1.0    | Mémoire épisodique sécurisée               |
| Vision Engine      | v1.0    | Extraction signaux visuels                 |
| Analysis Bot       | v3.2    | Contexte historique dans les rapports      |
| Quality Control    | v1.0    | Validation cohérence globale               |

---

## 📜 Conformité

MAGScore 7.0 est conforme à :
- **Constitution-MAGScore** : règles fondamentales de neutralité
- **Plan d'implémentation 7.0** : architecture cognitive validée
- **Principes RGPD** : aucune donnée personnelle stockée

---

## 📞 Support

Si vous rencontrez des difficultés :
1. Consultez ce README
2. Relisez les messages d'erreur
3. Vérifiez que votre environnement est correctement configuré
4. Lancez les tests pour identifier les problèmes

---

*This analysis describes dynamics only and is not a prediction.*

**MAGScore 7.0 — Cognitive Edition**  
*No Chance – Only Patterns*
