# Data cleansing 

- Detection des valeurs manquante:
        
        
        Strategie:
            - Supprimer les colonne dont toute les valeur son null, seul condition  la nature du feature dependant
            - Si une ligne atteint une moyen 50% de valeur null alors suppresion de la ligne ( on definis un thresh )
            - Remplacer le reste par les methode imputation moyen, ou logique metier si dependance 
        
        Observation:
        -   la comprehesnsion des donnees dit qu'il existe des valeurs manquante dans les Feature ( person_emp_length 2% , loan_int_rate  9% )
        -   on a utiliser l'analyse des patterns de valeurs manquantes pour se  decider sur la methode d'imputation
                - On s'est poser la question Est-ce que les autres variables peuvent prédire correctement la variable manquante ? si oui utiliser l'imputation multivarie
                - comme la moyenne des valeur manquante ne depasse pas les 20% l'approche multivarier n'est pas envisageable
        
        

        
      
       

            