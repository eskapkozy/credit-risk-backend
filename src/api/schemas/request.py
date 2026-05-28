import pandas as pd
from pydantic import BaseModel, Field, field_validator
from typing import Literal


from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Literal

'''
    On met en place des validation metier , pour eviter les incoherence dans les donnee , on cherche surtout les incherence temporelle
    incoherence humaine ( age, experience ) , coherence ( ratio ) montant des pret extreme
'''
class PredictRequest(BaseModel):

    model_config = ConfigDict(extra="forbid")

    # =========================
    # Informations personnelles
    # =========================

    person_age: int = Field(..., ge=18, le=100)

    person_income: float = Field(
        ...,
        gt=0,
        le=10_000_000
    )

    person_home_ownership: Literal[
        "RENT",
        "OWN",
        "MORTGAGE",
        "OTHER"
    ]

    person_emp_length: int = Field(
        ...,
        ge=0,
        le=60
    )

    # =========================
    # Informations crédit
    # =========================

    loan_intent: Literal[
        "PERSONAL",
        "EDUCATION",
        "MEDICAL",
        "VENTURE",
        "HOMEIMPROVEMENT",
        "DEBTCONSOLIDATION"
    ]

    loan_grade: Literal[
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G"
    ]

    loan_amnt: float = Field(
        ...,
        gt=0,
        le=5_000_000
    )

    loan_int_rate: float = Field(
        ...,
        ge=0,
        le=100
    )

    loan_percent_income: float = Field(
        ...,
        ge=0,
        le=1
    )

    cb_person_default_on_file: Literal["Y", "N"]

    cb_person_cred_hist_length: int = Field(
        ...,
        ge=0,
        le=80
    )

    # =====================================
    # VALIDATIONS CROISÉES / COHÉRENCE
    # =====================================

    @model_validator(mode="after")
    def validate_business_rules(self):

        # =====================================
        # 1. Historique de crédit impossible
        # =====================================

        possible_credit_history = self.person_age - 18

        if self.cb_person_cred_hist_length > possible_credit_history:
            raise ValueError(
                "Credit history length cannot exceed years since adulthood."
            )

        # =====================================
        # 2. Expérience de travail incohérente
        # =====================================

        working_years_possible = self.person_age - 14

        if self.person_emp_length > working_years_possible:
            raise ValueError(
                "Employment length exceeds realistic working years."
            )

        # =====================================
        # 3. Ratio prêt / revenu incohérent
        # =====================================

        computed_ratio = self.loan_amnt / self.person_income

        tolerance = 0.05

        if abs(computed_ratio - self.loan_percent_income) > tolerance:
            raise ValueError(
                "loan_percent_income is inconsistent with loan_amnt and person_income."
            )

        # =====================================
        # 4. Montant du prêt irréaliste
        # =====================================

        if self.loan_amnt > self.person_income * 20:
            raise ValueError(
                "Loan amount is unrealistically high compared to income."
            )

        # =====================================
        # 5. Taux incohérent avec le grade
        # =====================================

        grade_rate_rules = {
            "A": (0, 10),
            "B": (5, 15),
            "C": (10, 20),
            "D": (15, 25),
            "E": (20, 30),
            "F": (25, 40),
            "G": (30, 60),
        }

        min_rate, max_rate = grade_rate_rules[self.loan_grade]

        if not (min_rate <= self.loan_int_rate <= max_rate):
            raise ValueError(
                f"Interest rate inconsistent with loan grade {self.loan_grade}."
            )

        # =====================================
        # 6. Revenus faibles + propriété incohérente
        # =====================================

        if (
            self.person_income < 10_000
            and self.person_home_ownership == "OWN"
        ):
            raise ValueError(
                "Home ownership appears inconsistent with very low income."
            )

        # =====================================
        # 7. Jeune âge + historique long
        # =====================================

        if (
            self.person_age < 21
            and self.cb_person_cred_hist_length > 5
        ):
            raise ValueError(
                "Credit history too long for applicant age."
            )

        return self

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convertit le  request payload en pandas DataFrame.
        """

        return pd.DataFrame([self.model_dump()])


class PredictResponse(BaseModel):
    prediction: int
    probability: float
    threshold: float



