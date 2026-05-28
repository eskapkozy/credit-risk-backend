from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mlflow_tracking_uri: str = "http://mlflow:5000"
    run_id: str
    threshold: float = 0.25

    class Config:
        env_file = ".env"

settings = Settings()