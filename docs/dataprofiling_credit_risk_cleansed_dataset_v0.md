# PROFILING — Dataset credit_risk_cleansed_dataset_v0.csv

## Identification du type de dataset

**Type identifié : Dataset unique (Single Dataset)**

Ce dataset est un fichier plat où chaque ligne représente une observation unique (une demande de crédit). Toutes les variables sont déjà consolidées dans une seule table. Aucune jointure n'est nécessaire. La granularité est fixe et uniforme : une ligne = un emprunteur avec sa demande de crédit.

**Justification :**
- Structure tabulaire simple avec 31 833 observations et 13 variables
- Absence d'identifiant temporel ou de série chronologique
- Pas de clé de jointure vers d'autres tables
- Chaque ligne contient toutes les informations nécessaires pour une observation complète

---

## Étape 1 — Description des variables

| Nom technique | Définition métier | Rôle | Relation à la cible | Dépendances métier | Redondance | Statut réglementaire | Classe |
|---|---|---|---|---|---|---|---|
| **person_age** | Âge de l'emprunteur en années | Indépendante | Indirecte | Aucune | Non | Conforme | CAPACITÉ |
| **person_income** | Revenu annuel déclaré de l'emprunteur | Indépendante | Directe | Aucune | Non | Conforme | CAPACITÉ |
| **person_home_ownership** | Statut de propriété du logement (OWN, RENT, MORTGAGE, OTHER) | Indépendante | Indirecte | Aucune | Non | Conforme | CAPACITÉ |
| **person_emp_length** | Durée d'emploi actuelle en années | Indépendante | Indirecte | Aucune | Non | Conforme | CAPACITÉ |
| **loan_intent** | Finalité du prêt (EDUCATION, MEDICAL, PERSONAL, VENTURE, DEBTCONSOLIDATION, HOMEIMPROVEMENT) | Indépendante | Indirecte | Aucune | Non | Conforme | CONDITIONS |
| **loan_grade** | Note de risque attribuée au prêt (A à G) | Indépendante | Directe | Aucune | Non | Conforme | CONDITIONS |
| **loan_amnt** | Montant du prêt demandé | Indépendante | Directe | Aucune | Non | Conforme | CAPACITÉ |
| **loan_int_rate** | Taux d'intérêt appliqué au prêt (%) | Indépendante | Directe | Aucune | Non | Conforme | CONDITIONS |
| **loan_status** | Statut du prêt (0 = non défaut, 1 = défaut) | **Cible** | - | Aucune | Non | Conforme | - |
| **loan_percent_income** | Ratio montant du prêt / revenu annuel | Dérivée | Directe | loan_amnt / person_income | Oui (calculable) | Conforme | CAPACITÉ |
| **cb_person_default_on_file** | Historique de défaut dans le fichier de crédit (Y/N) | Indépendante | Directe | Aucune | Non | Conforme | COMPORTEMENT |
| **cb_person_cred_hist_length** | Durée de l'historique de crédit en années | Indépendante | Indirecte | Aucune | Non | Conforme | COMPORTEMENT |
| **age_groupe** | Catégorie d'âge regroupée (20-26, 26-30, etc.) | Dérivée | Indirecte | person_age | Oui (calculable) | Conforme | CAPACITÉ |

---

## Étape 2 — Classification des variables

### 2.1 Nature
- **Discrètes** : person_age, person_emp_length, loan_amnt, cb_person_cred_hist_length
- **Continues** : person_income, loan_int_rate, loan_percent_income
- **Catégorielles** : person_home_ownership, loan_intent, loan_grade, cb_person_default_on_file, age_groupe
- **Binaire** : loan_status, cb_person_default_on_file

### 2.2 Type
- **Numérique** : person_age, person_income, person_emp_length, loan_amnt, loan_int_rate, loan_percent_income, cb_person_cred_hist_length
- **Catégorielle** : person_home_ownership, loan_intent, loan_grade, cb_person_default_on_file, age_groupe
- **Binaire** : loan_status

### 2.3 Variabilité dans le temps
- **Statique** : person_age, age_groupe (à un instant T)
- **Dynamique - Compteur** : person_emp_length, cb_person_cred_hist_length (mesurent une durée)
- **Dynamique - Référence métier** : cb_person_default_on_file (historique de défaut)

### 2.4 Dimensionnalité
- **loan_percent_income** présente une redondance calculable à partir de loan_amnt et person_income
- **age_groupe** présente une redondance calculable à partir de person_age
- Les autres variables apportent une information métier distincte

---

## Statistiques descriptives

### Distribution des variables clés

**person_home_ownership :**
- RENT : 16 144 (50.8%)
- MORTGAGE : 13 069 (41.1%)
- OWN : 2 514 (7.9%)
- OTHER : 106 (0.3%)

**loan_intent :**
- EDUCATION : 6 264 (19.7%)
- MEDICAL : 5 946 (18.7%)
- PERSONAL : 5 409 (17.0%)
- VENTURE : 5 578 (17.5%)
- DEBTCONSOLIDATION : 5 094 (16.0%)
- HOMEIMPROVEMENT : 3 542 (11.1%)

**loan_grade :**
- A : 10 509 (33.0%)
- B : 10 214 (32.1%)
- C : 6 324 (19.9%)
- D : 3 548 (11.1%)
- E : 942 (3.0%)
- F : 236 (0.7%)
- G : 60 (0.2%)

**loan_status (cible) :**
- 0 (non défaut) : 24 875 (78.1%)
- 1 (défaut) : 6 958 (21.9%)

**cb_person_default_on_file :**
- N : 26 206 (82.3%)
- Y : 5 627 (17.7%)

---

## Conformité réglementaire

✅ **Toutes les variables sont conformes aux exigences réglementaires**

**Analyse de conformité :**
- Aucune variable protégée ou discriminante (origine ethnique, genre, religion, état de santé)
- Toutes les variables sont justifiables avec une raison métier explicite
- Les variables dérivées (loan_percent_income, age_groupe) exposent leur formule de calcul
- Les données sont vérifiables et traçables
- Aucune variable de décision institutionnelle détectée

---

## Recommandations préliminaires

1. **Variables à conserver** : Toutes les variables présentent un intérêt métier clair
2. **Variables dérivées** : loan_percent_income et age_groupe peuvent être recalculées si nécessaire
3. **Équilibre de la cible** : 21.9% de défaut - déséquilibre modéré à prendre en compte dans la modélisation
4. **Qualité des données** : Dataset propre, sans valeurs manquantes apparentes

---

## Prochaines étapes

Ce profiling constitue la base pour le **Feature Engineering Couche 1**. Les variables sont maintenant cartographiées et prêtes pour :

1. Analyse exploratoire approfondie
2. Création de features dérivées
3. Sélection de variables pertinentes
4. Construction du modèle de scoring
- **Date du profiling :** 4 mai 2026
- **Nombre d'observations :** 31 835
- **Nombre de variables :** 13

---

## Identification du type de dataset

**Type identifié : Dataset unique (Single Dataset)**

**Justification :** Le fichier contient une seule table plate où chaque ligne représente une observation unique (une demande de crédit). Il n'y a pas d'identifiant temporel ou de clé de jointure suggérant une structure longitudinale ou multi-source. Toutes les variables sont consolidées au niveau individuel.

---

## Étape 1 - Dictionnaire des variables

| Nom technique | Définition métier | Rôle | Relation à la cible | Dépendances métier | Redondance | Statut réglementaire | Classe correspondante |
|---|---|---|---|---|---|---|---|
| **person_age** | Âge du demandeur en années | Indépendante | Indirecte | Aucune | Partiellement redondant avec age_groupe | Conforme | CONDITIONS |
| **person_income** | Revenu annuel déclaré du demandeur | Indépendante | Directe | Aucune | Non | Conforme | CAPACITÉ |
| **person_home_ownership** | Statut de propriété du logement | Indépendante | Indirecte | Aucune | Non | Conforme | COLLATÉRAL |
| **person_emp_length** | Ancienneté professionnelle en années | Indépendante | Indirecte | Aucune | Non | Conforme | CONDITIONS |
| **loan_intent** | Objectif du prêt | Indépendante | Indirecte | Aucune | Non | Conforme | CONDITIONS |
| **loan_grade** | Note de risque interne du prêt | Dépendante | Directe | Calculée selon scoring interne | Non | Conforme | COMPORTEMENT |
| **loan_amnt** | Montant du prêt demandé | Indépendante | Directe | Aucune | Non | Conforme | CAPITALE |
| **loan_int_rate** | Taux d'intérêt appliqué au prêt | Dépendante | Directe | Calculé selon loan_grade et risque | Non | Conforme | CONDITIONS |
| **loan_status** | Statut de défaut (0=non, 1=oui) | **Cible** | - | Aucune | Non | Conforme | COMPORTEMENT |
| **loan_percent_income** | Ratio montant prêt / revenu | Dérivée | Directe | loan_amnt / person_income | Oui (calculable) | Conforme | CAPACITÉ |
| **cb_person_default_on_file** | Historique de défaut (Y/N) | Indépendante | Directe | Aucune | Non | Conforme | COMPORTEMENT |
| **cb_person_cred_hist_length** | Ancienneté historique crédit | Indépendante | Indirecte | Aucune | Non | Conforme | CONDITIONS |
| **age_groupe** | Catégorie d'âge regroupée | Dérivée | Indirecte | Calculée depuis person_age | Oui (redondant) | Conforme | CONDITIONS |

---

## Étape 2 - Classification des variables

### 2.1 Nature
- **Discrètes :** person_age, person_emp_length, loan_amnt, cb_person_cred_hist_length, age_groupe
- **Continues :** person_income, loan_int_rate, loan_percent_income
- **Catégorielles :** person_home_ownership, loan_intent, loan_grade, cb_person_default_on_file
- **Binaires :** loan_status, cb_person_default_on_file

### 2.2 Type
- **Numérique :** person_age, person_income, person_emp_length, loan_amnt, loan_int_rate, loan_percent_income, cb_person_cred_hist_length
- **Catégorielle :** person_home_ownership, loan_intent, loan_grade, cb_person_default_on_file, age_groupe
- **Binaire :** loan_status

### 2.3 Variabilité dans le temps
- **Statiques :** person_age, person_income, person_home_ownership, loan_intent, loan_amnt, age_groupe
- **Dynamiques (compteur) :** person_emp_length, cb_person_cred_hist_length
- **Dynamiques (calculées) :** loan_grade, loan_int_rate, loan_percent_income

### 2.4 Dimensionnalité
- **Haute dimensionnalité :** loan_percent_income (redondant, calculable)
- **Dimensionnalité moyenne :** Les autres variables apportent une information métier distincte

---

## Étape 3 - Limites structurelles du dataset

### 3.1 Limites identifiées par piliers

**CAPACITÉ :**
- ❌ Absence de charges fixes mensuelles
- ❌ Absence d'autres engagements de crédit en cours
- ❌ Absence de DTI (Debt-to-Income Ratio) global
- ❌ Revenu non vérifié (déclaratif seulement)

**CAPITALE :**
- ❌ Absence d'épargne ou actifs disponibles
- ❌ Absence d'apport personnel
- ❌ Absence de patrimoine net

**COLLATÉRAL :**
- ❌ Absence de valeur du bien immobilier
- ❌ Absence de garanties spécifiques
- ❌ Information limitée au statut de propriété seulement

**CONDITIONS :**
- ❌ Absence de type de contrat de travail
- ❌ Absence de secteur d'activité
- ❌ Absence de stabilité du revenu

**COMPORTEMENT :**
- ❌ Historique de crédit limité au défaut binaire
- ❌ Absence de détails sur incidents passés
- ❌ Absence de comportement de paiement

### 3.2 Moment du cycle de vie financier

**Snapshot à l'origination :** Les données correspondent à une demande de crédit initiale (origination). L'absence de dynamisme pur (évolution, dégradation) et la présence de variables de décision (loan_grade, loan_int_rate) confirment ce positionnement temporel.

### 3.3 Suggestions de proxies

Pour compenser les limites structurelles, les proxies suivants peuvent être construits :

- **Ratio d'endettement estimé :** loan_percent_income comme proxy du DTI global
- **Stabilité professionnelle :** person_emp_length comme proxy de la stabilité des revenus
- **Collateral indirect :** person_home_ownership comme proxy de la capacité à fournir des garanties
- **Antécédents de crédit :** cb_person_default_on_file comme proxy du comportement passé

---

## Étape 4 - Sélection métier préliminaire

### Variables pertinentes justifiées

**CAPACITÉ :**
- `person_income` - Fondamental pour évaluer la capacité de remboursement
- `loan_percent_income` - Ratio d'endettement direct

**CONDITIONS :**
- `person_age` - Facteur de stabilité et maturité financière
- `person_emp_length` - Stabilité professionnelle
- `person_home_ownership` - Stabilité résidentielle et collateral indirect
- `loan_intent` - Compréhension du besoin et risque associé

**COMPORTEMENT :**
- `cb_person_default_on_file` - Historique de comportement de crédit
- `loan_grade` - Évaluation risque interne

**CAPITALE :**
- `loan_amnt` - Exposition au risque

### Variables exclues avec justification

- `age_groupe` - **Redondant** : Information déjà disponible dans person_age
- `loan_int_rate` - **Variable de sortie** : Résultat du processus de décision, non d'entrée
- `cb_person_cred_hist_length` - **Valeur limitée** : Information partielle, faible pouvoir prédictif isolé

---

## Étape 5 - Variables sensibles et conformité

### Analyse réglementaire

Aucune variable protégée ou discriminante n'a été identifiée dans le dataset :

- ✅ **Absence de variables ethniques**
- ✅ **Absence de variables de genre**
- ✅ **Absence de variables de situation familiale**
- ✅ **Absence de variables religieuses**
- ✅ **Absence de variables d'état de santé**

Toutes les variables sont conformes aux exigences RGPD et aux réglementations européennes sur le crédit.

---

## Conclusion et approche analytique recommandée

### Recommandation : Analyse statique d'origination

Le dataset est adapté pour une modélisation de probabilité de défaut à l'origination avec les caractéristiques suivantes :

**Points forts :**
- Dataset complet et nettoyé
- Variables pertinentes pour les 5 piliers du crédit risk
- Conformité réglementaire assurée
- Taille d'échantillon suffisante (31 835 observations)

**Contraintes à accepter :**
- Informations limitées sur la capacité globale d'endettement
- Absence de détails sur le patrimoine et les garanties
- Historique de crédit simplifié

**Approche suggérée :**
1. **Feature engineering** basé sur les 8 variables retenues
2. **Création de variables composites** pour compenser les informations manquantes
3. **Modélisation supervisée** avec loan_status comme cible
4. **Validation croisée** pour assurer la robustesse du modèle

### Prochaine étape

Le dictionnaire de données est maintenant prêt pour passer au skill **Feature Engineering — Couche 1 : Fondamentaux Prudentiels**, en s'appuyant sur les 8 variables sélectionnées et les identifiées ci-dessus.

---

**Statut du profiling :** ✅ **TERMINÉ**
