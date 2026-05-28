# Credit Risk Modeling

## Problématique
Prédire le défaut de paiement en maximisant le recall (≥ 90%)
sous contrainte de précision métier.

## Architecture
WOE Pipeline → Ensemble hétérogène (stacking) → Threshold optimisé

## Résultats
| Modèle        | ROC-AUC | Recall | F1    | Threshold |
|---------------|---------|--------|-------|-----------|
| XGBoost       | 0.948   | 0.905  | 0.577 | 0.11      |
| LightGBM      | 0.92    | 0.91   | 0.59  | 0.15      |
| Ensemble      | 0.925   | 0.902  | 0.577 | 0.25      |  ← retenu

## Pourquoi l'ensemble ?
Threshold 0.25 vs 0.11 pour XGBoost → plus robuste en production

## Installation
pip install -r requirements.txt
mlflow server --host 127.0.0.1 --port 5000

## Usage
# Train
model = HETR(train_map=..., config_path=train_config)
model.run()

# Test
test = HETR(test_map=..., config_path=test_config)
test.run()

# Run server
uvicorn src.api.app:app --reload
