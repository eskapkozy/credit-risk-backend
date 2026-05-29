from fastapi import FastAPI
from src.api.router.predict import PredictRouter
from fastapi.middleware.cors import CORSMiddleware

# todo : creer un fichier de config qui contien les uri et paramettre de l'api, l'idee c'est de ne plus toucher le code brute

app = FastAPI()

predict_router = PredictRouter().register_routes()

# todo: corriger l'origini et utilise une variable d'environement

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #["http://localhost:5173"], #["http://localhost:3000"],  # ou "*" ajouter le serveur client
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router, prefix="/api")



