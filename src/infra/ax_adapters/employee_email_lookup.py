import json
from pathlib import Path

import pyodbc
from pyodbc import Connection

from src.utils.retry_decorator import retry_sync


class AxEmployeeEmailLookup:
    """Поиск email сотрудников на основе Microsoft Dynamics AX.

    Определяет адреса электронной почты по идентификаторам сотрудников,
    запрашивая базу данных AX через ODBC, с кэшем в JSON-файле, чтобы
    избежать повторных запросов. Соединение должно быть открыто с помощью
    :meth:`connect` перед поиском и закрыто с помощью :meth:`disconnect` после.
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
        """Инициализирует поиск.

        Args:
            odbc_driver: Имя используемого ODBC-драйвера.
            server: Хост сервера базы данных.
            database: Имя базы данных.
            username: Имя пользователя для аутентификации.
            password: Пароль для аутентификации.
            cache_path: Путь к файлу кэша JSON. По умолчанию
                ``data/user_cache.json``, если не указан.
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
        """Открывает ODBC-соединение с базой данных AX.

        Raises:
            RuntimeError: Если соединение уже установлено.
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
        """Закрывает ODBC-соединение, если оно открыто."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def _load_cache(self) -> dict[str, str]:
        """Загружает кэш email с диска.

        Returns:
            Кэшированное отображение идентификаторов сотрудников на email
            или пустой словарь, если файл кэша не существует.
        """
        if not self._cache_path.exists():
            return {}

        with self._cache_path.open('r', encoding='utf-8') as cache:
            return json.load(cache)

    def _save_cache(self, cache: dict[str, str]) -> None:
        """Сохраняет кэш email на диск.

        При необходимости создаёт родительские каталоги и записывает
        кэш в виде JSON в кодировке UTF-8 с отступами.

        Args:
            cache: Отображение идентификаторов сотрудников на email для сохранения.
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

    @retry_sync(count=3, delay=2)
    def get_email(self, employee_id: str) -> str | None:
        """Возвращает адрес электронной почты для указанного сотрудника.

        Сначала проверяет кэш; при промахе запрашивает базу данных AX
        и сохраняет результат в кэш. При возникновении исключения
        запрос повторяется до трёх раз с задержкой в 2 секунды между
        попытками (см. декоратор :func:`retry_sync`).

        Args:
            employee_id: Идентификатор сотрудника для поиска.

        Returns:
            Адрес электронной почты сотрудника или ``None``, если email не найден.

        Raises:
            RuntimeError: Если соединение с AX не установлено.
            Exception: Последнее исключение, возникшее после исчерпания
                всех попыток запроса.
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
