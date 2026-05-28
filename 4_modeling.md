## Architecture de l'ensemble

### Base learners
- LightGBM  : gradient boosting, signal non-linéaire
- XGBoost   : gradient boosting, régularisation différente
- RF        : bagging, variance réduite
- LogReg    : signal linéaire, nativement calibré
- SVM RBF   : frontières non-linéaires smooth

### Calibration
CalibratedClassifierCV (isotonic) sur RF
→ homogénéise les probabilités avant le méta-learner

### Méta-learner
LogisticRegression(C=1.0, class_weight={0:1, 1:8})
→ apprend à combiner les base learners
→ pénalise les faux négatifs

### Threshold
Optimisation sous contrainte :
  recall ≥ 0.90  ET  precision ≥ 0.20
→ threshold retenu : 0.25