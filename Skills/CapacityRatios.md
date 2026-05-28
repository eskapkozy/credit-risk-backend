# SKILL — Feature Engineering Couche 1 : Capacité de Remboursement

## Objectif

Permettre à l'agent de mesurer la **capacité de remboursement** d'un consumer à partir des variables disponibles, en produisant des ratios prudentiels interprétables et des features ML-ready.

Ce skill est le **premier skill d'analyse** après le DataProfiling. Il consomme obligatoirement les livrables du DataProfiling comme input.

---

## Orientation initiale — Demande obligatoire avant démarrage

Avant toute action, l'agent pose la question suivante à l'utilisateur :

> *"Avant de démarrer l'analyse de capacité, j'ai besoin du fichier de profiling produit par le skill DataProfiling. Pouvez-vous m'indiquer le chemin ou me fournir le fichier ?"*

L'agent **ne démarre pas** tant que l'utilisateur n'a pas fourni le fichier ou confirmé son emplacement.

---

## Lecture du dictionnaire de mapping

Une fois le fichier de profiling fourni, l'agent se rend à l'**Étape 1 — Dictionnaire des variables** du fichier DataProfiling.

C'est dans cette section que se trouve le mapping `concept métier → nom technique` pour ce dataset spécifique.

### Règle de lecture du dictionnaire

L'agent identifie et extrait les correspondances suivantes :

| Concept métier | Classe cherchée | Ce que l'agent cherche dans le dictionnaire |
|---|---|---|
| **Revenu** | CAPACITÉ | Variable indépendante de classe CAPACITÉ représentant le revenu |
| **Montant du prêt** | CAPITALE | Variable représentant le montant emprunté |
| **Ratio charge/revenu** | CAPACITÉ | Variable dérivée calculée comme montant / revenu |
| **Ancienneté emploi** | CONDITIONS | Variable représentant la durée en emploi |
| **Âge** | CONDITIONS | Variable représentant l'âge du consumer |

> ℹ️ L'agent utilise les noms techniques extraits du dictionnaire pour tous les calculs suivants. Il ne suppose jamais un nom de colonne sans l'avoir vérifié dans le dictionnaire.

### Règle d'interprétation

Pour chaque variable identifiée, l'agent vérifie :

- **Le rôle** : est-elle indépendante, dérivée ou dépendante ?
- **Le statut réglementaire** : conforme / sous réserve / exclue
- **Les dépendances** : est-elle calculée à partir d'autres variables ?
- **Les alertes leakage** : est-elle signalée dans le Livrable 7 ?

> ⚠️ Toute variable signalée comme leakage dans le Livrable 7 est **exclue automatiquement** des calculs, même si elle appartient à la classe CAPACITÉ.

---

## Prérequis obligatoires

Avant tout calcul, l'agent vérifie que les livrables suivants du DataProfiling sont disponibles :

- ✔ **Livrable 3** — Limites structurelles identifiées
- ✔ **Livrable 6** — Liste des variables pertinentes retenues
- ✔ **Livrable 7** — Alertes leakage documentées

> ⚠️ Si ces livrables sont absents, le skill doit être suspendu et le DataProfiling doit être exécuté en premier.

---

## Concept fondateur

La capacité de remboursement analyse la faculté de l'emprunteur à couvrir ses dettes.

> *Est-il en mesure de rembourser SANS difficulté ?*

**Distinction fondamentale à retenir :**

- **Endettement** = Pression existante sur le revenu
- **Capacité** = Aptitude à absorber cette pression

Ces deux notions sont liées mais distinctes. Un consumer peut être endetté et avoir une capacité suffisante — ou l'inverse. Le skill mesure les deux séparément avant de produire un diagnostic combiné.





---

## Étape 1 — Mapping de la pression (Prérequis au calcul)

Avant tout calcul de ratio, l'agent doit cartographier les éléments de pression disponibles.

### 1.1 Identifier les éléments de pression

L'agent cherche dans le dataset les variables suivantes :

| Élément | Variable idéale | Variable proxy acceptable |
|---|---|---|
| **Revenu réel** | Revenu vérifié mensuel | Revenu déclaratif annuel / 12 |
| **Charges fixes** | Loyer, assurances, charges récurrentes | Absent → signaler |
| **Engagements existants** | Total mensualités crédits en cours | Absent → signaler |
| **Mensualité du prêt demandé** | Mensualité calculée | loan_amnt comme proxy si absent |

### 1.2 Règle de décision

```
SI revenu + charges + engagements disponibles
   → MODE COMPLET : calcul des ratios réels

SI revenu disponible MAIS charges ou engagements absents
   → MODE PROXY : calcul partiel avec proxies
   → DOCUMENTER les limites explicitement

SI revenu absent
   → BLOQUER : calcul impossible
   → REMONTER alerte : "Capacité non mesurable — revenu absent"
```

> ⚠️ L'agent ne calcule jamais silencieusement. Toute limite est documentée dans le livrable.

### 1.3 Stabilité du revenu

Avant de valider le revenu comme input, l'agent évalue sa fiabilité :

- `person_emp_length` disponible → signal de stabilité professionnelle
- Revenu déclaratif non vérifié → signaler comme donnée à risque
- Absence de type de contrat → limite structurelle à noter

---

## Étape 2 — Calcul des ratios fondamentaux

### Ratio 1 — DTI (Debt-to-Income Ratio)
**Mesure de pression**

```
DTI = Total dettes / Revenu
```

**Lecture :**
- `< 35%` → Pression maîtrisée
- `35% - 50%` → Zone de vigilance
- `> 50%` → Pression excessive → risque élevé

**En mode proxy (données incomplètes) :**
```
DTI_proxy = loan_amnt / person_income
```
> ⚠️ Ce ratio est partiel — il ne couvre que le prêt demandé, pas les engagements existants. Le documenter explicitement.

---

### Ratio 2 — DSTI (Debt Service to Income)
**Mesure de capacité**

```
DSTI = Mensualité du prêt / Revenu mensuel
```

**Lecture :**
- `< 30%` → Charge supportable → OK
- `30% - 40%` → Zone prudentielle → surveiller
- `> 40%` → Charge excessive → RISK

**En mode proxy :**
```
DSTI_proxy = loan_percent_income
```
> ℹ️ Si `loan_percent_income` est déjà disponible dans le dataset, l'utiliser directement. Vérifier qu'il est calculé comme `loan_amnt / person_income`.

---

### Ratio 3 — Residual Income
**Mesure de survie financière**

```
Residual_Income = Revenu mensuel - Charges fixes - Mensualité
```

**Lecture :**
- Positif suffisant → Consumer viable après paiement
- Positif faible → Marge de manœuvre réduite → fragile
- Négatif → Insolvabilité structurelle

**En mode proxy :**
```
Residual_Income_proxy = (person_income / 12) * (1 - loan_percent_income)
```
> ⚠️ Cette estimation ignore les charges fixes. Elle mesure le revenu résiduel après mensualité uniquement — pas après charges de vie.

---

## Étape 3 — Variables dérivées ML-ready

L'agent produit les features suivantes, prêtes pour la modélisation :

| Feature | Formule | Type | Interprétation |
|---|---|---|---|
| `dti_proxy` | `loan_amnt / person_income` | Continue | Pression d'endettement estimée |
| `dsti_proxy` | `loan_percent_income` | Continue | Charge mensuelle relative |
| `residual_income_proxy` | `(person_income/12) * (1 - loan_percent_income)` | Continue | Revenu résiduel estimé après mensualité |
| `income_stability_score` | `person_emp_length / (person_age - 18)` | Continue | Part de la vie active en emploi stable |
| `loan_to_annual_income` | `loan_amnt / person_income` | Continue | Exposition relative au revenu annuel |
| `capacity_pressure_flag` | `1 si dsti_proxy > 0.40 sinon 0` | Binaire | Alerte charge excessive |

> ⚠️ Ces features sont créées **avant le split** train/test. Les transformations (normalisation, encoding) s'appliquent **après le split**, uniquement sur le train, puis transférées au test.

---

## Étape 4 — Diagnostic de capacité

Sur la base des ratios calculés, l'agent produit un diagnostic synthétique :

| Niveau | Condition | Interprétation |
|---|---|---|
| ✅ **SAINE** | DSTI < 30% ET Residual Income > 0 | Consumer viable, capacité confirmée |
| ⚠️ **SOUS PRESSION** | DSTI 30-40% OU Residual Income faible | Capacité limitée, surveiller |
| ❌ **CRITIQUE** | DSTI > 40% OU Residual Income < 0 | Capacité insuffisante, risque élevé |

> ℹ️ Les seuils sont des **paramètres**, pas des constantes. Ils doivent être adaptés selon le produit, le marché et le cadre réglementaire local.

---

## Étape 5 — Limites et signalement

L'agent documente systématiquement :

### Ce qui est mesuré réellement
- DSTI proxy basé sur le prêt demandé uniquement
- Revenu déclaratif non vérifié

### Ce qui n'est pas mesuré
- Charges fixes réelles → absentes du dataset
- Engagements crédit existants → absents du dataset
- Stabilité et nature du revenu → non vérifiable

### Impact sur la fiabilité du modèle
> *Un DTI et un DSTI calculés sans les engagements existants sous-estiment systématiquement la pression réelle sur le consumer. Le modèle PD peut sous-estimer le risque pour les consumers multi-endettés non visibles dans ce dataset.*

---

## Livrables attendus

### Livrable C1 — Table des ratios calculés
Pour chaque observation : `dti_proxy`, `dsti_proxy`, `residual_income_proxy`, `income_stability_score`, `loan_to_annual_income`, `capacity_pressure_flag`

### Livrable C2 — Diagnostic de capacité
Distribution des niveaux SAINE / SOUS PRESSION / CRITIQUE sur la population.

### Livrable C3 — Rapport de limites
Mode de calcul utilisé (COMPLET / PROXY / BLOQUÉ), variables manquantes, impact estimé sur la fiabilité.

### Livrable C4 — Features ML-ready
Dataset enrichi avec les nouvelles colonnes, prêt pour le split et la modélisation.

---

## Transition vers le skill suivant

Ce skill est terminé lorsque les 4 livrables sont produits.

L'agent peut ensuite activer le skill **Feature Engineering — Couche 2 : Endettement et Levier**, qui mesurera la pression globale d'endettement du consumer.

> ✔ Les features de capacité doivent être présentes dans le dataset avant d'activer le skill suivant.
