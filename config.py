from pydantic import BaseSettings

class Settings(BaseSettings):
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"
    
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "notifications"
    POSTGRES_USER: str = "admin"
    POSTGRES_PASS: str = "admin"
    
    API_KEY: str = ""
    
    EMAIL_SMTP_HOST: str = "smtp.gmail.com"
    EMAIL_SMTP_PORT: int = 587
    EMAIL_USER: str = ""
    EMAIL_PASS: str = ""
    
    SMS_API_KEY: str = ""
    SMS_API_SECRET: str = ""
    
    FIREBASE_CREDENTIALS_PATH: str = "firebase-config.json"
    
    class Config:
        env_file = ".env"

settings = Settings()
