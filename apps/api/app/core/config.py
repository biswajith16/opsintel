from dataclasses import dataclass
import os

DATASET_VERSION = "2026.08.28.v1"
SCENARIO_VERSION = "2026.08.28.v1"
FEATURE_VERSION = "v1"
MODEL_VERSION = "v1"


@dataclass(frozen=True)
class Settings:
    demo_seed: int = int(os.getenv("DEMO_SEED", "20260828"))
    cors_allowed_origins: tuple[str, ...] = tuple(
        item.strip() for item in os.getenv(
            "CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
        ).split(",") if item.strip()
    )
    api_version: str = "0.1.0"


settings = Settings()
