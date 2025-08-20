from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Chift(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="CHIFT_", extra="ignore"
    )
    client_secret: str = Field(default=...)
    client_id: str = Field(default=...)
    account_id: str = Field(default=...)
    url_base: str | None = "https://api.chift.eu"
    consumer_id: str | None = None


class Config:
    chift = Chift()


config: Config = Config()
