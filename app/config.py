from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    fw_file: str = "main_fw.py"
    root_key: str = "3bb09ac6-0252-462d-8cdb-84e9677435fa"
    root_email: str = "root@example.com"
    sqlite_database_url: str = "sqlite+aiosqlite:///thermo.db"


settings = Settings()
