from pydantic import (
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    # postgres
    COFFETLDB_DRIVER: str = ''
    COFFETLDB_SERVER: str = ''
    COFFETLDB_PORT: int = 5432
    COFFETLDB_USER: str = ''
    COFFETLDB_PASSWORD: str = ''
    COFFETLDB_NAME: str = ''

    @computed_field
    @property
    def COFFETL_DATABASE_URI(self) -> str:
        return str(
            MultiHostUrl.build(
                scheme=self.COFFETLDB_DRIVER,
                username=self.COFFETLDB_USER,
                password=self.COFFETLDB_PASSWORD,
                host=self.COFFETLDB_SERVER,
                port=self.COFFETLDB_PORT,
                path=self.COFFETLDB_NAME,
            )
        )

    # # duckdb
    # DUCKDB_PATH: str
    # DUCKDB_SECRET_TYPE: str
    # DUCKDB_SECRET_NAME: str

    # @computed_field
    # @property
    # def DUCKDB_SECRET_STRING(self) -> str:
    #     return f"""
    #         TYPE {self.DUCKDB_SECRET_TYPE},
    #         HOST '{self.COFFETLDB_SERVER}',
    #         PORT {self.COFFETLDB_PORT},
    #         DATABASE {self.COFFETLDB_NAME},
    #         USER '{self.COFFETLDB_USER}',
    #         PASSWORD '{self.COFFETLDB_PASSWORD}'
    #     """
