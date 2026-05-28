from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.router.predict import PredictRouter


# ==========================================
# Mock inference service
# ==========================================

class MockInferenceService:

    def predict(self, data):

        return {
            "prediction": 1,
            "probability": 0.82,
            "threshold": 0.5
        }


# ==========================================
# FastAPI test app
# ==========================================

app = FastAPI()

predict_router = PredictRouter(
    inference_service=MockInferenceService()
)

app.include_router(
    predict_router.register_routes()
)

client = TestClient(app)


# ==========================================
# Valid payload
# ==========================================

VALID_PAYLOAD = {
    "person_age": 35,
    "person_income": 54000,
    "person_home_ownership": "RENT",
    "person_emp_length": 10,
    "loan_intent": "PERSONAL",
    "loan_grade": "B",
    "loan_amnt": 12000,
    "loan_int_rate": 11.5,
    "loan_percent_income": 0.22,
    "cb_person_default_on_file": "N",
    "cb_person_cred_hist_length": 8
}


# ==========================================
# Happy path
# ==========================================

def test_predict_success():

    response = client.post(
        "/predict",
        json=VALID_PAYLOAD
    )

    assert response.status_code == 200

    data = response.json()

    assert data["prediction"] == 1
    assert data["probability"] == 0.82
    assert data["threshold"] == 0.5


# ==========================================
# Missing field
# ==========================================

def test_missing_field():

    payload = VALID_PAYLOAD.copy()

    del payload["loan_amnt"]

    response = client.post(
        "/predict",
        json=payload
    )

    assert response.status_code == 422


# ==========================================
# Invalid category
# ==========================================

def test_invalid_loan_grade():

    payload = VALID_PAYLOAD.copy()

    payload["loan_grade"] = "Z"

    response = client.post(
        "/predict",
        json=payload
    )

    assert response.status_code == 422


# ==========================================
# Invalid age
# ==========================================

def test_invalid_age():

    payload = VALID_PAYLOAD.copy()

    payload["person_age"] = 12

    response = client.post(
        "/predict",
        json=payload
    )

    assert response.status_code == 422


# ==========================================
# Negative income
# ==========================================

def test_negative_income():

    payload = VALID_PAYLOAD.copy()

    payload["person_income"] = -1000

    response = client.post(
        "/predict",
        json=payload
    )

    assert response.status_code == 422


# ==========================================
# Credit history inconsistency
# ==========================================

def test_credit_history_inconsistency():

    payload = VALID_PAYLOAD.copy()

    payload["person_age"] = 20
    payload["cb_person_cred_hist_length"] = 15

    response = client.post(
        "/predict",
        json=payload
    )

    assert response.status_code == 422


# ==========================================
# Employment inconsistency
# ==========================================

def test_employment_length_inconsistency():

    payload = VALID_PAYLOAD.copy()

    payload["person_age"] = 22
    payload["person_emp_length"] = 15

    response = client.post(
        "/predict",
        json=payload
    )

    assert response.status_code == 422


# ==========================================
# Loan ratio inconsistency
# ==========================================

def test_loan_percent_income_inconsistency():

    payload = VALID_PAYLOAD.copy()

    payload["person_income"] = 10000
    payload["loan_amnt"] = 5000
    payload["loan_percent_income"] = 0.90

    response = client.post(
        "/predict",
        json=payload
    )

    assert response.status_code == 422


# ==========================================
# Interest rate inconsistency
# ==========================================

def test_interest_rate_grade_inconsistency():

    payload = VALID_PAYLOAD.copy()

    payload["loan_grade"] = "A"
    payload["loan_int_rate"] = 45

    response = client.post(
        "/predict",
        json=payload
    )

    assert response.status_code == 422


# ==========================================
# Extra forbidden field
# ==========================================

def test_extra_field_forbidden():

    payload = VALID_PAYLOAD.copy()

    payload["unexpected_field"] = "hack"

    response = client.post(
        "/predict",
        json=payload
    )

    assert response.status_code == 422