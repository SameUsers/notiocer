import json

import pytest

from src.infra.ax_adapter.employee_email_lookup import AxEmployeeEmailLookup


@pytest.fixture
def lookup(tmp_path):
    return AxEmployeeEmailLookup(
        odbc_driver="test-driver", server="test-server", database="test-database",
        username="test-user", password="test-password", cache_path=tmp_path / "cache.json",
    )


def test_get_email_reads_cache_without_connecting(lookup, tmp_path, mocker):
    (tmp_path / "cache.json").write_text(json.dumps({"EMP-001": "cached@example.com"}), encoding="utf-8")
    connect = mocker.patch("src.infra.ax_adapter.employee_email_lookup.pyodbc.connect")

    assert lookup.get_email("EMP-001") == "cached@example.com"
    connect.assert_not_called()


def test_get_email_queries_identifier_and_caches_result(lookup, tmp_path, mocker, monkeypatch):
    connection = mocker.patch("src.infra.ax_adapter.employee_email_lookup.pyodbc.connect").return_value
    cursor = connection.cursor.return_value
    cursor.fetchone.return_value = ("EMP-001", "active", "department", "employee@example.com", "working")
    lookup.connect()
    monkeypatch.chdir(tmp_path)

    assert lookup.get_email("EMP-001") == "employee@example.com"
    assert cursor.execute.call_args.args[1] == "EMP-001"
    assert "et.EMPLID = ?" in cursor.execute.call_args.args[0]
    cursor.close.assert_called_once_with()
    assert json.loads((tmp_path / "cache.json").read_text(encoding="utf-8")) == {"EMP-001": "employee@example.com"}
    assert lookup.get_email("EMP-001") == "employee@example.com"
    cursor.execute.assert_called_once()
    lookup.disconnect()
    connection.close.assert_called_once_with()


@pytest.mark.parametrize("row", [None, ("EMP-001", None, None, None), ("EMP-001", None, None, "")])
def test_get_email_returns_none_for_missing_address(lookup, tmp_path, mocker, row):
    connection = mocker.patch("src.infra.ax_adapter.employee_email_lookup.pyodbc.connect").return_value
    cursor = connection.cursor.return_value
    cursor.fetchone.return_value = row
    lookup.connect()

    assert lookup.get_email("EMP-001") is None
    cursor.close.assert_called_once_with()
    assert not (tmp_path / "cache.json").exists()


def test_get_email_closes_cursor_on_query_error(lookup, mocker):
    connection = mocker.patch("src.infra.ax_adapter.employee_email_lookup.pyodbc.connect").return_value
    cursor = connection.cursor.return_value
    query_error = RuntimeError("Query failed")
    cursor.execute.side_effect = query_error
    lookup.connect()

    with pytest.raises(RuntimeError) as error:
        lookup.get_email("EMP-001")

    assert error.value is query_error
    cursor.close.assert_called_once_with()
