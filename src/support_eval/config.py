"""Configuration, with credentials excluded from stored experiment settings."""
import os
from pathlib import Path
from dotenv import dotenv_values
from pydantic import BaseModel, Field, SecretStr


class Settings(BaseModel):
    fireworks_api_key: SecretStr = Field(default=SecretStr(''), exclude=True, repr=False)
    langsmith_api_key: SecretStr = Field(default=SecretStr(''), exclude=True, repr=False)
    model: str = 'accounts/fireworks/models/muse-spark-open'
    project: str = 'week4-support-muse-spark'
    endpoint: str = 'https://api.smith.langchain.com'
    workspace_id: str = ''
    budget_usd: float = Field(default=3.0, gt=0, le=3.0)
    max_tokens: int = Field(default=1024, gt=0, le=4096)
    temperature: float = 0.0
    timeout_seconds: float = 60.0
    integration_verified: bool = False

    def require_credentials(self):
        missing = [name for name in ('fireworks_api_key', 'langsmith_api_key')
                   if not getattr(self, name).get_secret_value().strip()]
        if missing:
            raise ValueError('Configure local credentials: ' + ', '.join(missing))

    def model_settings(self) -> dict:
        return dict(model=self.model, max_tokens=self.max_tokens, temperature=self.temperature,
                    timeout_seconds=self.timeout_seconds, max_retries=0, structured_method='json_schema')


def load_settings(path: Path = Path('.env')) -> Settings:
    values = {**dotenv_values(path), **os.environ}
    mapping = {'fireworks_api_key': 'FIREWORKS_API_KEY', 'langsmith_api_key': 'LANGSMITH_API_KEY',
               'model': 'FIREWORKS_MODEL', 'project': 'LANGSMITH_PROJECT',
               'endpoint': 'LANGSMITH_ENDPOINT', 'workspace_id': 'LANGSMITH_WORKSPACE_ID',
               'budget_usd': 'PROJECT_BUDGET_USD', 'max_tokens': 'MODEL_MAX_TOKENS',
               'integration_verified': 'INTEGRATION_VERIFIED'}
    return Settings(**{field: values[key] for field, key in mapping.items() if values.get(key)})
