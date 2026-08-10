# Système expert flou — Estimation du risque de paludisme (prototype pédagogique)

Travail pratique de logique floue — Université de Kinshasa, Faculté des Sciences et
Technologies, Mention Mathématiques, Statistique et Informatique.

**Auteurs :** MUBIALA KIESE SAMUEL, LUVETO DIALUNGANA SALOMON, WABA MPWO EXAUCE

## ⚠️ Avertissement

Ce dépôt contient un **prototype pédagogique** développé dans le cadre d'un cours de
logique floue. Il illustre le fonctionnement des modèles d'inférence floue de **Mamdani**
et de **Sugeno** appliqués (à titre d'exemple) à l'estimation d'un risque de paludisme à
partir de trois symptômes simplifiés (température, fatigue, maux de tête). La base de
règles n'a pas été validée par un professionnel de santé. **Ce projet ne doit en aucun cas
être utilisé pour un diagnostic médical réel.**

## Contenu du dépôt

| Fichier | Description |
|---|---|
| `fuzzy_paludisme.py` | Implémentation manuelle complète (fuzzification, règles, Mamdani avec centre de gravité par intégration numérique, Sugeno, étude comparative, analyse de sensibilité, benchmark de temps d'exécution) |
| `streamlit_app.py` | Interface web interactive pour tester le système |
| `requirements.txt` | Dépendances Python |
| `rapport/main.tex` | Rapport LaTeX complet |
| `figures/` | Graphiques générés par le script (fonctions d'appartenance, sensibilité) |

## Installation et exécution locale

```bash
git clone https://github.com/<votre-compte>/paludisme-flou.git
cd paludisme-flou
pip install -r requirements.txt

# Lancer l'étude complète (génère les tableaux et graphiques) :
python fuzzy_paludisme.py

# Lancer l'interface web interactive :
streamlit run streamlit_app.py
```

## Déploiement

L'application est déployable gratuitement sur
[Streamlit Community Cloud](https://streamlit.io/cloud) :
1. Pousser ce dépôt sur GitHub (public).
2. Se connecter sur share.streamlit.io avec le compte GitHub.
3. Sélectionner le dépôt et le fichier `streamlit_app.py` comme point d'entrée.
4. Déployer — l'application est accessible via une URL publique en quelques minutes.

## Méthodologie

Aucune bibliothèque d'inférence floue (ex. `scikit-fuzzy`) n'a été utilisée : la
fuzzification, l'activation des règles, l'implication, l'agrégation et la défuzzification
(centre de gravité par intégration numérique pour Mamdani ; moyenne pondérée pour Sugeno)
sont entièrement implémentées à la main dans `fuzzy_paludisme.py`.

## Licence

Projet académique — usage pédagogique uniquement.
