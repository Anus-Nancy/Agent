from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TCF Complaint Management API"
    api_prefix: str = "/api/v1"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/tcf"
    escalation_check_interval_minutes: int = 10
    sentence_transformer_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    query_similarity_threshold: float = 0.85
    faiss_index_path: str = "./backend/artifacts/faiss/query.index"
    faiss_metadata_path: str = "./backend/artifacts/faiss/query_meta.json"
    policy_docs_path: str = "./backend/knowledge_base/policies"
    kb_faiss_index_path: str = "./backend/artifacts/faiss/kb.index"
    kb_faiss_metadata_path: str = "./backend/artifacts/faiss/kb_meta.json"
    llm_model_name: str = "google/flan-t5-small"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
