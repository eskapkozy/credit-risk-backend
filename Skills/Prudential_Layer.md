# Credit Risk Feature Framework — Couche 1 : Fondamentaux Prudentiels

## 🎯 Objectif

Poser un cadre structuré pour la construction de features en credit risk retail, conforme aux exigences réglementaires.

Cette couche constitue :

* le **socle prudentiel obligatoire**
* un **référentiel interprétable**
* une base utilisable par des **agents IA sous contraintes réglementaires**

---

## 🧠 Principe de construction

La construction des features suit une logique par couches :

* **Couche 1 (actuelle)** : Fondamentaux prudentiels (réglementaire + interprétable)
* Couches suivantes : dynamique, comportement, optimisation ML

👉 Cette couche est **non négociable** :

* règles déterministes
* métriques explicables
* seuils contrôlables

---

## ⚖️ Contraintes réglementaires globales

Tout agent IA doit respecter :

* ✔ Vérification de la capacité de remboursement
* ✔ Prévention du surendettement
* ✔ Interprétabilité des décisions
* ✔ Utilisation de données vérifiables
* ✔ Application de règles prudentes (hard constraints)

---

# 🔵 PILIER 1 — CAPACITY (Capacité de remboursement)

## 🎯 Objectif

Évaluer si le client peut rembourser sans difficulté financière.

---

## 📏 Métriques prudentielles clés

### 1. Debt-to-Income (DTI)

* Formule : dette mensuelle / revenu
* Seuil :

  * ≤ 40% → acceptable
  * > 40% → risque élevé
* Interprétabilité : pression de la dette sur le revenu

---

### 2. Disposable Income

* Formule : revenu - charges - dettes
* Seuil :

  * > 0 → acceptable
  * ≤ 0 → refus
* Interprétabilité : marge financière réelle

---

### 3. Payment-to-Income (PTI)

* Formule : mensualité du nouveau prêt / revenu
* Seuil :

  * ≤ 30% → acceptable
  * > 30% → vigilance
* Interprétabilité : impact du nouveau crédit

---

## 🔄 Métriques dynamiques

* income_volatility
* income_trend
* liquidity_buffer

---

## 🔗 Interactions / extensions

* DTI × income_volatility
* PTI × liquidity_buffer

---

## 🚫 Règles prudentielles

* DTI trop élevé → refus ou ajustement
* revenu instable → haircut obligatoire
* reste à vivre insuffisant → refus

---

# 🟢 PILIER 2 — LEVERAGE (Endettement)

## 🎯 Objectif

Mesurer le niveau d’exposition globale à la dette.

---

## 📏 Métriques prudentielles clés

### 1. Total Debt

* Formule : somme des encours
* Seuil : dépend du revenu (relatif)
* Interprétabilité : niveau global d’endettement

---

### 2. Credit Utilization

* Formule : crédit utilisé / limite totale
* Seuil :

  * < 50% → sain
  * 50–80% → vigilance
  * > 80% → risque élevé
* Interprétabilité : pression court terme

---

### 3. Number of Loans

* Seuil :

  * élevé → signal de risque
* Interprétabilité : fragmentation de la dette

---

## 🔄 Métriques dynamiques

* debt_growth_rate
* recent_credit_openings
* revolving_dependency

---

## 🔗 Interactions / extensions

* utilization × income_volatility
* total_debt × disposable_income

---

## 🚫 Règles prudentielles

* utilisation excessive → alerte forte
* accumulation rapide de dettes → pénalité
* multi-endettement → restriction

---

# 🟡 PILIER 3 — COLLATERAL (Garantie)

## 🎯 Objectif

Évaluer la capacité de récupération en cas de défaut.

---

## 📏 Métriques prudentielles clés

### 1. Loan-to-Value (LTV)

* Formule : prêt / valeur collatéral
* Seuil :

  * ≤ 80% → sain
  * 80–100% → vigilance
  * > 100% → refus
* Interprétabilité : couverture du prêt

---

### 2. Adjusted Collateral Value

* Formule : valeur × (1 - haircut)
* Règle :

  * haircut obligatoire selon type d’actif
* Interprétabilité : valeur prudente

---

### 3. Coverage Ratio

* Formule : valeur ajustée / prêt
* Seuil :

  * ≥ 1.2 → confortable
  * < 1.0 → risque élevé
* Interprétabilité : niveau de protection

---

## 🔄 Métriques dynamiques

* stress_LTV
* collateral_depreciation_rate
* collateral_liquidity_score

---

## 🔗 Interactions / extensions

* LTV × income_volatility
* collateral_liquidity × default_risk

---

## 🚫 Règles prudentielles

* absence de haircut → non conforme
* collatéral non liquide → pénalité forte
* collatéral ≠ substitut à capacity

---

# 🔴 PILIER 4 — STABILITY (Stabilité)

## 🎯 Objectif

Évaluer la durabilité de la situation financière.

---

## 📏 Métriques prudentielles clés

### 1. Job Tenure

* Seuil :

  * < 6 mois → risque élevé
  * > 24 mois → stable
* Interprétabilité : continuité du revenu

---

### 2. Income Volatility

* Formule : écart-type / moyenne
* Seuil :

  * > 50% → instable
* Interprétabilité : variabilité du revenu

---

### 3. Stable Income Ratio

* Formule : revenu stable / revenu total
* Seuil :

  * < 40% → risque élevé
* Interprétabilité : qualité du revenu

---

## 🔄 Métriques dynamiques

* income_trend
* income_drop_flag
* income_frequency

---

## 🔗 Interactions / extensions

* income_volatility × DTI
* income_trend × leverage

---

## 🚫 Règles prudentielles

* revenu instable → haircut
* chute de revenu → blocage ou revue
* tenure faible → restriction

---

# 🤖 Utilisation par un agent IA

L’agent doit :

1. Prioriser les métriques de cette couche
2. Respecter les seuils comme contraintes strictes
3. Garantir l’interprétabilité
4. Ne pas contourner les règles via optimisation ML

---

# 🚀 Conclusion

Cette couche constitue :

* un **socle réglementaire**
* un **cadre d’interprétation**
* une **base fiable pour le feature engineering**

👉 Toute feature avancée doit être :

* dérivée de cette couche
* explicable par rapport à ces métriques
* conforme aux règles prudentielles
