from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from .logging import *


class Configs(BaseSettings):
    JOBINJA_USERNAME: str | None = None
    JOBINJA_PASSWORD: str | None = None
    DATABASE_URL: str | None = None
    CONFIG_PATH: str | None = None

    model_config = SettingsConfigDict(env_file=".env")


project_configs = Configs()


if project_configs.CONFIG_PATH and not os.path.exists(project_configs.CONFIG_PATH):
    os.makedirs(project_configs.CONFIG_PATH)
