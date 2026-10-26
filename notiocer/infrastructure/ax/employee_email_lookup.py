import json
from pathlib import Path
from tempfile import NamedTemporaryFile

import pyodbc
from pyodbc import Connection

from notiocer.infrastructure.retry import retry


class AxEmployeeEmailLookup:
    """Ищет email сотрудников в AX через ODBC и сохраняет найденные адреса в JSON-кэше."""

    def __init__(
        self,
        odbc_driver: str,
        server: str,
        database: str,
        username: str,
        password: str,
        cache_path: Path | None = None,
    ) -> None:
        """Принимает параметры AX и путь к кэшу, по умолчанию data/user_cache.json."""
        self._odbc_driver = odbc_driver
        self._server = server
        self._database = database
        self._username = username
        self._password = password
        self._cache_path = (
            cache_path if cache_path is not None else Path('data/user_cache.json')
        )
        self._connection: Connection | None = None

    def connect(self) -> None:
        """Открывает соединение с AX.

        Raises:
            RuntimeError: Соединение уже открыто.
        """
        if self._connection is not None:
            raise RuntimeError('Соединение уже установлено')

        connection_string = (
            f'DRIVER={{{self._odbc_driver}}};'
            f'SERVER={self._server};'
            f'DATABASE={self._database};'
            f'UID={self._username};'
            f'PWD={self._password};'
            'TrustServerCertificate=yes;'
        )

        self._connection = pyodbc.connect(connection_string)

    def disconnect(self) -> None:
        """Закрывает соединение с AX, если оно открыто."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def _load_cache(self) -> dict[str, str]:
        """Читает JSON-кэш или возвращает пустой словарь, если файла нет."""
        if not self._cache_path.exists():
            return {}

        try:
            with self._cache_path.open('r', encoding='utf-8') as cache_file:
                cached_emails = json.load(cache_file)
        except json.JSONDecodeError as error:
            raise ValueError(
                f'Некорректный JSON-кэш email: {self._cache_path}'
            ) from error
        if not isinstance(cached_emails, dict) or any(
            not isinstance(employee_id, str) or not isinstance(email_address, str)
            for employee_id, email_address in cached_emails.items()
        ):
            raise ValueError(
                f'Кэш email должен содержать строковые идентификаторы и адреса: {self._cache_path}'
            )
        return cached_emails

    def _save_cache(self, cached_emails: dict[str, str]) -> None:
        """Атомарно заменяет JSON-кэш, создавая недостающие каталоги."""
        self._cache_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        temporary_path: Path | None = None
        try:
            with NamedTemporaryFile(
                mode='w',
                encoding='utf-8',
                dir=self._cache_path.parent,
                prefix=f'.{self._cache_path.name}.',
                suffix='.tmp',
                delete=False,
            ) as cache_file:
                temporary_path = Path(cache_file.name)
                json.dump(cached_emails, cache_file, ensure_ascii=False, indent=4)
            temporary_path.replace(self._cache_path)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    @retry(attempts=3, delay_seconds=2)
    def get_email(self, employee_id: str) -> str | None:
        """Ищет email в кэше и AX, возвращая None при отсутствии адреса.

        Raises:
            RuntimeError: Адрес не закэширован и соединение с AX не открыто.
        """
        cached_emails = self._load_cache()
        if employee_id in cached_emails:
            return cached_emails[employee_id]
        if self._connection is None:
            raise RuntimeError('Соединение с AX не установлено')
        query_path = Path(__file__).with_name('queries') / 'employee_email.sql'
        query = query_path.read_text(encoding='utf-8')
        cursor = self._connection.cursor()
        try:
            cursor.execute(query, employee_id)
            employee_record = cursor.fetchone()
            if employee_record is None or not employee_record[3]:
                return None
            email_address = str(employee_record[3])
        finally:
            cursor.close()
        cached_emails[employee_id] = email_address
        self._save_cache(cached_emails)
        return email_address
