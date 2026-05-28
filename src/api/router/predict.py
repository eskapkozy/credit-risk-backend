
from fastapi import APIRouter


from src.api.schemas.request import PredictResponse, PredictRequest
from src.api.service.inference import Inference

router = APIRouter()

class PredictRouter:

    def __init__(self):
        data_ = 'data'


    def register_routes(self):

        @router.post("/predict", response_model=PredictResponse)
        def predict(request: PredictRequest):

            inference = Inference()

            result = inference.predict(request.to_dataframe())

            return PredictResponse(
                prediction=result["prediction"],
                probability=result["probability"],
                threshold=result["threshold"]
            )

        return router