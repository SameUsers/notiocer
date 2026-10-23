from datetime import timedelta
from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class InvoiceSelectionSettings(BaseModel):
    allowed_categories: set[str] = {"Д0", "Д1", "Д2", "Д3", "Д4", "Д5", "Д60"}
    minimum_invoice_age: timedelta = timedelta(days=3)


class AppSettings(BaseSettings):
    invoice_selection: InvoiceSelectionSettings = Field(default_factory=InvoiceSelectionSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_nested_delimiter="__"
    )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()

