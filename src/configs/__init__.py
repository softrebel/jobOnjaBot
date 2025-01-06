from pydantic_settings import BaseSettings, SettingsConfigDict


class Configs(BaseSettings):
    JOBINJA_USERNAME: str | None = None
    JOBINJA_PASSWORD: str | None = None

    model_config = SettingsConfigDict(env_file=".env")


project_configs = Configs()
