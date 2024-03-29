import os

import pytest
from pydantic import ValidationError

from sql_mock.clickhouse.column_mocks import Int
from sql_mock.clickhouse.table_mocks import ClickHouseTableMock
from sql_mock.table_mocks import table_meta


@table_meta(table_ref="mock_test_table")
class MockTestTable(ClickHouseTableMock):
    id = Int(default=1)


@pytest.fixture(autouse=True)
def patch_os_environment_variables(mocker):
    mocker.patch.dict(
        os.environ,
        {
            "SQL_MOCK_CLICKHOUSE_USER": "test_user",
            "SQL_MOCK_CLICKHOUSE_PASSWORD": "test_password",
            "SQL_MOCK_CLICKHOUSE_HOST": "test_host",
            "SQL_MOCK_CLICKHOUSE_PORT": "9000",
        },
        clear=True,
    )


def test_init_with_environment_variables(patch_os_environment_variables):
    """
    ...then the env vars should be used to set the attributes
    """
    table = MockTestTable()
    assert table.settings.host == "test_host"
    assert table.settings.user == "test_user"
    assert table.settings.password == "test_password"
    assert table.settings.port == "9000"


def test_init_with_missing_configs(mocker):
    """
    ...then it should raise an error
    """
    with pytest.raises(ValidationError):
        mocker.patch.dict(
            os.environ,
            {},
            clear=True,
        )
        MockTestTable()


def test_get_results(mocker):
    """
    Test the _get_results method.
    """
    mock_client = mocker.patch("sql_mock.clickhouse.table_mocks.clickhouse_connect.get_client")
    mock_query_result = [{"column1": "value1", "column2": 42}]
    query = "SELECT 1, 2"

    mock_result = mocker.MagicMock()
    mock_result.result_rows = [("value1", 42)]
    mock_result.column_names = ("column1", "column2")
    mock_client.return_value.__enter__.return_value.query.return_value = mock_result

    instance = ClickHouseTableMock()
    result = instance._get_results(query=query)

    assert result == mock_query_result
    mock_client.return_value.__enter__.return_value.query.assert_called_once_with(query, use_none=True)
