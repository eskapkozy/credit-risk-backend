# Dataset Dictionnaire 


   | features                  | types   | description                         | dependance                     |
|--------------------------|--------|-------------------------------------|--------------------------------|
| person_age               | int    | Age des individus                   | No                             |
| person_income            | int    | Revenu des individus                | No                             |
| person_home_ownership    | str    | Situation de domicile               | No                             |
| person_emp_length        | float  | Expérience de travail               | No                             |
| loan_intent              | str    | Intention de prêt                   | No                             |
| loan_grade               | str    | Note du prêt                        | No                             |
| loan_amnt                | int    | Montant du prêt                     | No                             |
| loan_int_rate            | float  | Taux d'intérêt du prêt              | No                             |
| loan_status              | binaire| Statut du prêt (défaut / non)       | No                             |
| loan_percent_income      | float  | % du prêt dans le revenu            | person_income & loan_amnt      |
| cb_person_default_on_file| str    | Historique de défaut                | No                             |
| cb_person_cred_hist_length| int   | Longueur de l'historique de crédit  | No                             |                 | No                        |
    



