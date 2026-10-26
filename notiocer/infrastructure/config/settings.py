from collections.abc import Callable
from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
    SecretStr,
    StringConstraints,
    field_validator,
)
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


def resolve_project_path(path: Path) -> Path:
    """Разрешает относительный путь от корня проекта."""
    return path if path.is_absolute() else PROJECT_ROOT / path


class InvoiceReportFileSettings(BaseModel):
    """Путь к исходному отчёту XLS или XLSX."""

    path: Path = PROJECT_ROOT / 'workdir/DZ_Report.xls'

    @field_validator('path')
    @classmethod
    def validate_path(cls, value: Path) -> Path:
        """Проверяет расширение отчёта и разрешает относительный путь."""
        if value.suffix.lower() not in {'.xls', '.xlsx'}:
            raise ValueError('Отчёт должен иметь расширение .xls или .xlsx')
        return resolve_project_path(value)


class InvoiceSelectionSettings(BaseModel):
    """Категории и минимальный возраст счёта по точному времени."""

    allowed_categories: set[NonEmptyString] = Field(
        default={'Д0', 'Д1', 'Д2', 'Д3', 'Д4', 'Д5', 'Д60'},
        min_length=1,
    )
    minimum_invoice_age: timedelta = Field(default=timedelta(days=3), ge=timedelta(0))


class EmailMessageSettings(BaseModel):
    """Тема и текст письма; прежние mail_subject и mail_tex поддерживаются как имена настроек."""

    subject: NonEmptyString = Field(
        default='Неполученные предоплаты до загрузки',
        validation_alias=AliasChoices('subject', 'mail_subject'),
    )
    body: NonEmptyString = Field(
        default="""Добрый день.
Направляем список счетов с неполученной предоплатой до загрузки.

В рассылку включаются счета старше установленного минимального возраста.
Возраст рассчитывается по точному времени выставления счёта.

Просим обеспечить поступление оплаты от Клиента или предоставить СФБ пояснение
и запланированную Клиентом дату платежа.

При некорректных данных или невозможности получения оплаты просим сообщить
об этом на почтовую группу СФБ.""",
        validation_alias=AliasChoices('body', 'mail_tex'),
    )


class ExchangeSettings(BaseModel):
    """Обязательные учётные данные Exchange; пароль не имеет значения по умолчанию."""

    username: NonEmptyString
    password: SecretStr = Field(min_length=1)


class AxSettings(BaseModel):
    """Обязательные параметры AX и путь к локальному кэшу адресов."""

    odbc_driver: NonEmptyString = 'ODBC Driver 17 for SQL Server'
    server: NonEmptyString
    database: NonEmptyString
    username: NonEmptyString
    password: SecretStr = Field(min_length=1)
    cache_path: Path = PROJECT_ROOT / 'data/user_cache.json'

    @field_validator('cache_path')
    @classmethod
    def validate_cache_path(cls, value: Path) -> Path:
        """Разрешает путь к кэшу от корня проекта."""
        return resolve_project_path(value)


class AppSettings(BaseSettings):
    """Настройки из окружения и корневого .env; вложенные поля разделяются через __."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / '.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        env_nested_delimiter='__',
        hide_input_in_errors=True,
    )

    ax: AxSettings
    exchange: ExchangeSettings
    invoice_selection: InvoiceSelectionSettings = Field(
        default_factory=InvoiceSelectionSettings
    )
    message: EmailMessageSettings = Field(default_factory=EmailMessageSettings)
    invoice_report_file: InvoiceReportFileSettings = Field(
        default_factory=InvoiceReportFileSettings
    )
    mailing_rules_file: Path = PROJECT_ROOT / 'config/invoice_routing_rules.yml'

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[Callable[[], dict[str, Any]], ...]:
        """Приводит старые имена message к новым до объединения источников."""

        def normalize_message_aliases(
            source: PydanticBaseSettingsSource,
        ) -> Callable[[], dict[str, Any]]:
            def read_source() -> dict[str, Any]:
                source_values = source()
                message_values = source_values.get('message')
                if isinstance(message_values, dict):
                    message_values = message_values.copy()
                    for legacy_name, canonical_name in [
                        ('mail_subject', 'subject'),
                        ('mail_tex', 'body'),
                    ]:
                        if legacy_name in message_values:
                            value = message_values.pop(legacy_name)
                            message_values.setdefault(canonical_name, value)
                    source_values = {**source_values, 'message': message_values}
                return source_values

            return read_source

        return tuple(
            normalize_message_aliases(source)
            for source in (
                init_settings,
                env_settings,
                dotenv_settings,
                file_secret_settings,
            )
        )

    @field_validator('mailing_rules_file')
    @classmethod
    def validate_rules_path(cls, value: Path) -> Path:
        """Разрешает путь к YAML от корня проекта."""
        return resolve_project_path(value)


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Один раз загружает и проверяет настройки приложения."""
    return AppSettings()  # type: ignore
