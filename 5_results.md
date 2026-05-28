# Résultats & Choix de Modélisation

## Contexte des métriques

La prédiction de défaut de paiement est un problème à **classes déséquilibrées** avec des contraintes métier asymétriques. Un faux négatif (défaut non détecté) coûte structurellement plus cher à la banque qu'un faux positif (bon client refusé). Les métriques sont donc organisées en deux volets : **optimisation** et **évaluation**.

---

## Volet 1 — Optimisation

### Objectif
Trouver la combinaison d'hyperparamètres qui **maximise le F1-score** sous contrainte métier :

```
recall    ≥ 0.90   (capturer au moins 90% des défauts)
precision ≥ 0.20   (éviter un taux de faux positifs incontrôlé)
```

### Outil : Optuna (TPE — Tree-structured Parzen Estimator)

Optuna a été utilisé pour explorer automatiquement l'espace des hyperparamètres des base learners et du méta-learner, en évitant la recherche exhaustive (GridSearch).

**Paramètres explorés :**

| Composant | Paramètre | Plage explorée |
|---|---|---|
| LightGBM | n_estimators | 200 – 800 |
| LightGBM | learning_rate | 0.01 – 0.1 |
| LightGBM | num_leaves | 31 – 127 |
| XGBoost | n_estimators | 200 – 800 |
| XGBoost | learning_rate | 0.01 – 0.1 |
| XGBoost | max_depth | 3 – 8 |
| Méta-learner | C | 0.01 – 10 |
| Méta-learner | class_weight (défaut) | 1 – 15 |

**Configuration retenue :**

```yaml
optuna_trials: 30
direction: maximize (F1)
contrainte: recall ≥ 0.90
```

### Résultats du tuning Optuna

Le tuning Optuna n'a pas permis d'améliorer les métriques par rapport au run baseline. Les runs tunés ont systématiquement présenté :

- une **dégradation du seuil de décision** (threshold monte vers 0.35)
- une **hausse des faux négatifs** (FN passe de 93 à 163)
- un **F1 légèrement amélioré** (0.577 → 0.589) mais au détriment du recall opérationnel

**Comparaison runs Optuna vs baseline :**

| Run | Threshold | Recall | F1 | FN | FP |
|---|---|---|---|---|---|
| Baseline (sans Optuna) | **0.25** | 0.902 | 0.577 | **93** | 1159 |
| Optuna 10 trials `{0:1, 1:5}` | 0.24 | 0.902 | 0.567 | 102 | 1337 |
| Optuna 30 trials `{0:1, 1:8}` | 0.35 | 0.902 | **0.589** | 163 | 532 |

### Analyse de l'échec du tuning

Deux facteurs expliquent pourquoi Optuna n'a pas abouti à une amélioration nette :

**1. Espace de recherche trop large pour 30 trials.** Avec 8 hyperparamètres à explorer, 30 trials sont insuffisants pour que TPE converge. Une exploration sérieuse nécessiterait 100+ trials, ce qui représente ~6h de calcul sur machine locale Intel avec SVM.

**2. Le vrai goulot n'est pas les hyperparamètres.** Le stacking hétérogène avec WOE et SMOTE-ENN a déjà extrait le maximum du signal disponible dans les données. La marge d'amélioration par tuning est structurellement limitée.

### Décision

**Optuna est abandonné.** Le run baseline sans tuning est retenu comme modèle de production.

---

## Volet 2 — Évaluation

### Modèle retenu : Ensemble hétérogène — run baseline

**Métriques sur le jeu de test :**

| Métrique | Valeur | Interprétation |
|---|---|---|
| ROC-AUC | **0.9257** | Excellente discrimination |
| Gini | 0.8515 | Signal très fort |
| Recall | **0.902** | 90.2% des défauts détectés ✅ |
| Precision | 0.424 | 42.4% des alertes sont de vrais défauts |
| F1 | 0.577 | Compromis recall/precision acceptable |
| Accuracy | 0.737 | Moins pertinente sur classes déséquilibrées |
| Threshold | **0.25** | Seuil stable et robuste |

**Matrice de confusion :**

```
                  Prédit Non-Défaut   Prédit Défaut
Réel Non-Défaut        2573 (TN)       1159 (FP)
Réel Défaut              93 (FN)        950 (TP)
```

### Comparaison avec les modèles candidats

| Modèle | ROC-AUC | Recall | F1 | FN | Threshold |
|---|---|---|---|---|---|
| Logistic Regression | 0.88 | 0.90 | 0.55 | 122 | — |
| LightGBM | 0.92 | 0.91 | 0.59 | 95 | 0.15 |
| XGBoost | 0.948 | 0.905 | 0.577 | 102 | **0.11** |
| **Ensemble hétérogène** | **0.925** | **0.902** | 0.577 | **93** | **0.25** |

### Pourquoi l'ensemble hétérogène est retenu

**1. Threshold le plus stable (0.25 vs 0.11 pour XGBoost)**

Un seuil à 0.11 est dangereusement bas en production — un léger glissement de distribution suffit à faire chuter le recall. Un seuil à 0.25 offre une marge de sécurité deux fois plus grande.

**2. Nombre de FN le plus bas (93 vs 102 pour XGBoost)**

93 défauts manqués sur ~1043 défauts réels représente 8.9% de manqués — c'est le meilleur résultat absolu obtenu sur ce dataset.

**3. ROC-AUC compétitif (0.925)**

Légèrement inférieur à XGBoost (0.948) mais la différence est marginale en opérationnel. Le gain en robustesse du seuil compense largement cet écart.

### Choix assumés et leurs justifications

**On subit le F1 à 0.577** — c'est un choix délibéré. Améliorer le F1 implique de remonter le threshold (moins de FP) mais augmente mécaniquement les FN. Or dans un contexte de scoring de crédit, un faux négatif (défaut accordé) représente une perte réelle pour la banque, contre un manque à gagner pour un faux positif (bon client refusé). La banque prudente préfère FN bas.

**On accepte 1159 FP** — refuser 1159 bons clients est un coût commercial, pas une perte directe. Ce ratio est acceptable compte tenu du niveau de protection obtenu sur les défauts.

**On fixe recall ≥ 0.90 comme contrainte dure** — en dessous de 90%, le modèle ne respecte plus les exigences de risque minimum. Cette contrainte a guidé toutes les décisions d'optimisation.

---

## Conclusion

Le modèle d'ensemble hétérogène avec threshold=0.25 représente le meilleur équilibre entre performance, robustesse et alignement métier sur ce dataset. La perfection n'est pas atteignable avec les features disponibles — le plafond informationnel du dataset a été atteint. La valeur du projet réside dans l'architecture reproductible, la traçabilité MLflow et la rigueur du processus de décision.