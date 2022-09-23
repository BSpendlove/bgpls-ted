from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "bgpls-ted"
    app_version: str = "0.0.1"
    mongodb_uri: str = "mongodb://root:example@localhost:27017"

settings = Settings()
