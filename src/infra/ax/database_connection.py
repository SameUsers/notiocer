import pyodbc
from pyodbc import Connection


class AxDatabaseConnection:
    def __init__(
        self,
        odbc_driver: str,
        server: str,
        database: str,
        username: str,
        password: str,
    ) -> None:
        self._odbc_driver = odbc_driver
        self._server = server
        self._database = database
        self._username = username
        self._password = password
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
