import json
from pathlib import Path

import pyodbc
from pyodbc import Connection


class AxEmployeeEmailLookup:
    """Employee email lookup backed by Microsoft Dynamics AX.

    Resolves employee identifiers to email addresses by querying the AX
    database over ODBC, with a JSON file cache to avoid repeated lookups.
    The connection must be opened with :meth:`connect` before lookups
    and closed with :meth:`disconnect` afterwards.
    """

    def __init__(
        self,
        odbc_driver: str,
        server: str,
        database: str,
        username: str,
        password: str,
        cache_path: Path | None = None,
    ) -> None:
        """Initialize the lookup.

        Args:
            odbc_driver: Name of the ODBC driver to use.
            server: Database server host.
            database: Database name.
            username: Username for authentication.
            password: Password for authentication.
            cache_path: Path to the JSON cache file. Defaults to
                ``data/user_cache.json`` when not provided.
        """
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
        """Open the ODBC connection to the AX database.

        Raises:
            RuntimeError: If a connection is already established.
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
        """Close the ODBC connection if it is open."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def _load_cache(self) -> dict[str, str]:
        """Load the email cache from disk.

        Returns:
            The cached mapping of employee identifiers to emails, or an
            empty dict if the cache file does not exist.
        """
        if not self._cache_path.exists():
            return {}

        with self._cache_path.open('r', encoding='utf-8') as cache:
            return json.load(cache)

    def _save_cache(self, cache: dict[str, str]) -> None:
        """Persist the email cache to disk.

        Creates parent directories as needed and writes the cache as
        UTF-8 JSON with indentation.

        Args:
            cache: Mapping of employee identifiers to emails to persist.
        """
        self._cache_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        with self._cache_path.open('w', encoding='utf-8') as file:
            json.dump(
                cache,
                file,
                ensure_ascii=False,
                indent=4,
            )

    def get_email(self, employee_id: str) -> str | None:
        """Return the email address for the given employee.

        Checks the cache first; on a miss, queries the AX database and
        stores the result in the cache.

        Args:
            employee_id: Identifier of the employee to look up.

        Returns:
            The employee's email address, or ``None`` if no email is found.

        Raises:
            RuntimeError: If the AX connection is not established.
        """
        cache = self._load_cache()
        if employee_id in cache:
            return cache[employee_id]
        if self._connection is None:
            raise RuntimeError('Соединение с AX не установлено')
        query_path = Path(__file__).resolve().parents[3] / 'sql/get_emloye_email.sql'
        query = query_path.read_text(encoding='utf-8')
        cursor = self._connection.cursor()
        try:
            cursor.execute(query, employee_id)
            result = cursor.fetchone()
            if result is None or not result[3]:
                return None
            email = str(result[3])
        finally:
            cursor.close()
        cache[employee_id] = email
        self._save_cache(cache)
        return email
