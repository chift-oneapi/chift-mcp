from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from chift_mcp.constants import DEFAULT_CONFIG


class Chift(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="CHIFT_", extra="ignore"
    )
    client_secret: str
    client_id: str
    account_id: str
    function_config: dict | None = DEFAULT_CONFIG
    url_base: str | None = "https://api.chift.eu"


class Config:
    chift = Chift()


config: Config = Config()
