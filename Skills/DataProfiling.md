# SKILL — Compréhension et Cartographie du Dataset

## Objectif

Permettre à l'agent de prendre connaissance d'un dataset, d'identifier le sens métier de chaque variable, ses dépendances, et de produire un **dictionnaire de données structuré**.

Ce skill est le **prérequis obligatoire** avant toute construction de features. Il doit être exécuté intégralement avant d'invoquer tout autre skill (notamment le skill Feature Engineering Couche 1).

---

## Contraintes réglementaires globales

Avant toute analyse, l'agent doit respecter les obligations suivantes :

- ✔ Aucune variable **protégée ou discriminante** ne peut être utilisée comme feature (ex : origine ethnique, genre, situation familiale, religion, état de santé — conformément au RGPD, à la directive européenne sur le crédit, et aux réglementations locales applicables)
- ✔ Toute variable retenue doit être **justifiable et documentée** avec une raison métier explicite
- ✔ Les variables dérivées doivent exposer leur **formule de calcul** de manière transparente
- ✔ Les données utilisées doivent être **vérifiables et traçables** jusqu'à leur source
- ✔ Toute variable à caractère sensible identifiée doit être **signalée et exclue** avant de passer à l'étape suivante

> ⚠️ En cas de doute sur la conformité d'une variable, l'agent doit la **signaler comme variable sous réserve** et ne pas l'intégrer au dictionnaire sans validation humaine.

---






## Identification du type de dataset

Avant toute cartographie, l'agent identifie la structure du dataset parmi les trois types suivants :

### 1. Dataset unique (Single Dataset)
Un seul fichier plat où chaque ligne représente une observation unique (un client, une demande de crédit). Toutes les variables sont déjà consolidées. Aucune jointure n'est nécessaire. La granularité est fixe et uniforme.

### 2. Dataset longitudinal (Panel Data)
Un même identifiant (client, contrat) apparaît sur plusieurs lignes correspondant à différentes périodes. Permet de capturer l'évolution dans le temps. L'agent doit identifier la dimension temporelle (date, mois, snapshot) et savoir agréger ou pivoter selon le besoin analytique.

### 3. Dataset croisé (Cross Dataset / Multi-source)
Plusieurs tables indépendantes reliées par des clés de jointure (ex : `client_id`, `contract_id`). Chaque table possède sa propre granularité et sa propre logique métier. L'agent doit cartographier les relations entre tables, vérifier la cohérence des clés, et identifier les risques de duplication ou de perte d'information lors des jointures.

> L'agent documente le type identifié et justifie son choix avant de poursuivre.

---

## Étape 1 — Description des variables

Pour chaque variable, l'agent documente les éléments suivants :

| Champ | Description |
|---|---|
| **Nom technique** | Nom exact de la variable dans le dataset |
| **Définition métier** | Ce que la variable représente dans le contexte business |
| **Rôle** | Cible / Indépendante / Dépendante / Dérivée |
| **Relation à la cible** | Directe / Indirecte / Inconnue |
| **Dépendances métier** | Est-elle calculée à partir d'autres variables ? Si oui, laquelle formule ? |
| **Redondance** | Existe-t-il une autre variable exprimant la même information ? |
| **Statut réglementaire** | Conforme / Sous réserve / Exclue |
| **Classe correspondante** | rattacher a une classe de la liste de pilier [ CAPACITÉ, COMPORTEMENT, CAPITALE, COLLATÉRAL, CONDITIONS] |

**Définitions des rôles :**

- **Variable cible** : la variable que le modèle cherche à expliquer ou prédire (ex : défaut de paiement, probabilité de défaut)
- **Variable indépendante** : variable observée ou mesurée qui exerce une influence sur la cible. Elle n'est pas calculée à partir d'autres variables du dataset
- **Variable dépendante** : variable dont la valeur est influencée par d'autres variables du dataset (hors cible)
- **Variable dérivée** : variable construite à partir d'autres variables par une formule explicite

*Exemple : `person_income` représente le revenu mensuel déclaré du client. Variable indépendante. Influence directe sur la capacité de remboursement. Utilisée dans le calcul du DTI, PTI et Disposable Income. Statut : conforme.*

*Exemple : `bmi` (Indice de Masse Corporelle) est une variable dérivée calculée comme le poids divisé par le carré de la taille. Elle mesure la corpulence d'un individu. Statut : sous réserve en credit risk — nécessite validation réglementaire avant utilisation.*

---

## Étape 2 — Classification des variables

Chaque variable est classifiée selon quatre dimensions :

### 2.1 Nature
- **Discrète** : valeurs dénombrables et distinctes (ex : nombre de crédits en cours, nombre d'incidents de paiement)
- **Continue** : valeurs mesurables sur un intervalle (ex : revenu, montant du prêt, ratio DTI)

### 2.2 Type
- Numérique (entier ou décimal)
- Catégorielle (modalités nommées, ex : type d'emploi, secteur d'activité)
- Binaire (deux états, ex : défaut oui/non, propriétaire oui/non)
- Date / Temporelle

### 2.3 Variabilité dans le temps

- **Statique** : valeur fixe ou très rarement mise à jour (ex : date de naissance, numéro de contrat). Une donnée issue d'un processus batch n'est pas nécessairement statique — la distinction repose sur la nature de la variable, pas sur le mode d'alimentation.
- **Dynamique** : valeur qui évolue dans le temps. Deux sous-types à distinguer :
  - **Série temporelle** : enregistrement périodique d'une ou plusieurs variables dans le temps. Peut être analysée de manière univariée (une seule variable) ou multivariée (plusieurs variables simultanément). Exemples : historique de paiement mensuel, évolution du solde de crédit, variation du revenu.
  - **Streaming** : donnée produite en continu et en temps réel. Nécessite une infrastructure et une logique d'analyse spécifiques, différentes des données batch. Exemples : transactions en temps réel, alertes comportementales immédiates.
  - **Reference metier** : La lecture du dynamisme se fait selon les contexte suivante:
        - **Historique** : Ce qui c'est passé avant , daté, donnée bureau , défaut passé, c'est un stock d'information
        - **Compteur**   : Combien de fois, depuis combien de temps. c'est une fréquence encodée dans une variable statique, pas de trajectoire jutste une magnitude
        - **Dynamise-pur** : Evolution entre deux snapshot Delta T1 & T2 . Une Acceleration , degradation, stabilité. il n'existe que dans une serie Temporelle
> ⚠️ La présence de variables dynamiques (séries temporelles ou streaming) conditionne l'approche d'analyse. L'agent doit les signaler explicitement.

### 2.4 Dimensionnalité
La variable apporte-t-elle une information réellement nouvelle, ou est-elle fortement corrélée à des variables existantes ? Cette évaluation est métier à ce stade — la validation statistique interviendra dans une couche ultérieure.


### 2.5 Ratacher la variable

- **classe** : chaque variable est rattacher a l'une des classe de la liste [ CAPACITÉ, COMPORTEMENT, CAPITALE, COLLATÉRAL, CONDITIONS]

---
## Étape 3 — Identifier La limite structurel

L'agent se pose des question sur la limite structurel des données fournis

**Reference metier:**
    
- **Definition** : la limite structurel represente toute informations que le modele ne vois pas, en realite les moedle ne comprenent pas la realite, il ne saisisse pas le sens metier, si une information importante n'est pas donnee alors elle n'existe pas pour le modele
- **Exemple** : Pour un modele de probabilite de defaut On ne dispose pas d'information suivante 
        -**revenu**
        -**charge fixe**
        -**Engagement courant**
        -**Que comprendre ?:** ces information sont importante pour juger la capacite de remboursement, le laverage . si il ne sont pas fournis le modele peut continuer a voir des correlation significative, predire un defaut avec des information limite conduit a des biais

### 3.1 Listé les Limites 

-**Capacité rembourssemnt** : Quel information Capital sur la capacite de rembourssement n'est pas disponible ?
-**Endettement** : Abscence d'information sur les engament precedente  ? 
-**Capitale** : Quel information sur la capitale n'est pas disponible ?
-**Collateral** : Abscence d'information sur le collateral  ? 
-**Conditions** : Quel information sur les conditions n'est pas disponible ?
-**Stabilité** : Quel information sur la stabilité n'est pas disponible ?
-**Fiabilité** : Quel information sur la fiabilité n'est pas disponible ?

### 3.2 Identifier le moment du cycle de vie financier 

Repondre a une seul question, a quel moment du cycle de vie financier  correspond ce snapshot ?

-**est a l'origination?** on reconnais une origination par la presence de decision,une absence de dynamisme pur ( information sur la degradation, volatilite ). 
-**est ce une evolution ?** est ce une periode Tn apres l'origination ? . dans un cas ou on dois suivre l'evolution ou performance de credit d'un client , on a des snapshot qui represente un instant T, comparer a un autre snapshot on peu realiser la tache de distinction


        




## Étape 4 — Sélection métier préliminaire

À l'issue de la cartographie, l'agent identifie les variables **utiles et justifiées** par rapport à la cible, selon les indicateurs clés du profil client en credit risk retail.

> ⚠️ Toute variable retenue doit être accompagnée d'une justification métier explicite. "Utile" ne constitue pas une justification suffisante dans un cadre réglementaire.

Les indicateurs de référence sont :

| Indicateur | Variables typiquement associées |
|---|---|
| **Capacité** | Revenu, charges, DTI, PTI, Disposable Income |
| **Stabilité** | Ancienneté emploi, volatilité du revenu, type de contrat |
| **Fiabilité** | Historique de défaut, comportement de paiement, incidents passés |
| **Risque** | Notation interne/externe, nombre de crédits, exposition globale |

La sélection à ce stade est **exclusivement basée sur la compréhension métier**. La validation statistique (corrélation, importance, tests) interviendra dans les couches suivantes.

---

## Livrables attendus

L'agent doit produire à l'issue de ce skill :

### Livrable 1 — Dictionnaire des variables
Pour chaque variable : nom, définition métier, type, nature, rôle, dépendances, variabilité dans le temps, statut réglementaire, classe correspondante.

### Livrable 2 — Classification du dataset
Structure identifiée (single / longitudinal / cross), dimensionnalité globale, présence ou absence de séries temporelles ou de données streaming.

### Livrable 3 — Limite structurel du dataset
Pour chaque mesure : information manquante et leur impacte,suggerer des proxy interpretable, notifier le moment de cycle de vie du dataset

### Livrable 4 — Liste des variables exclues
Variables écartées pour motif réglementaire, avec justification explicite pour chacune.

### Livrable 5 — Conclusion sur l'approche d'analyse
Sur la base des livrables 1 et 2, l'agent formule une recommandation sur l'approche analytique adaptée (analyse statique, temporelle, multi-source) avant de passer au skill suivant.

### Livrable 6 — Liste préliminaire des variables pertinentes
Variables retenues pour la construction des features, avec justification métier pour chacune.

### Livrable 7 — Alerte sur du leakage
L'agent Alert et identifie les variable suceptible d'entrainer un leakage, il justifie pourquoi ? , identifie le type de leakage


---

## Transition vers le skill suivant

Ce skill est terminé lorsque les 5 livrables sont produits et validés.

L'agent peut ensuite activer le skill **Feature Engineering — Couche 1 : Fondamentaux Prudentiels**, en s'appuyant sur le dictionnaire et la classification produits ici.

> ✔ Aucune feature ne peut être construite sans que ce skill ait été complété.