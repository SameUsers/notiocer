import json
from pathlib import Path

import pyodbc
from pyodbc import Connection


class AxEmployeeEmailLookup:
    def __init__(
        self,
        odbc_driver: str,
        server: str,
        database: str,
        username: str,
        password: str,
        cache_path: Path | None = None,
    ) -> None:
        self._odbc_driver = odbc_driver
        self._server = server
        self._database = database
        self._username = username
        self._password = password
        self._cache_path = cache_path if cache_path is not None else Path("data/user_cache.json")
        self._connection: Connection | None = None

    def connect(self) -> None:
        if self._connection is not None:
            raise RuntimeError("Соединение уже установлено")

        connection_string = (
            f"DRIVER={{{self._odbc_driver}}};"
            f"SERVER={self._server};"
            f"DATABASE={self._database};"
            f"UID={self._username};"
            f"PWD={self._password};"
            "TrustServerCertificate=yes;"
        )

        self._connection = pyodbc.connect(connection_string)

    def disconnect(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def _load_cache(self) -> dict[str, str]:
        if not self._cache_path.exists():
            return {}

        with self._cache_path.open("r", encoding="utf-8") as cache:
            return json.load(cache)

    def _save_cache(self, cache: dict[str, str]) -> None:
        self._cache_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        with self._cache_path.open("w", encoding="utf-8") as file:
            json.dump(
                cache,
                file,
                ensure_ascii=False,
                indent=4,
            )

    def get_email(self, employee_id: str) -> str | None:
        cache = self._load_cache()
        if employee_id in cache:
            return cache[employee_id]
        if self._connection is None:
            raise RuntimeError("Соединение с AX не установлено")
        query_path = Path(__file__).resolve().parents[3] / "sql/get_emloye_email.sql"
        query = query_path.read_text(encoding="utf-8")
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
