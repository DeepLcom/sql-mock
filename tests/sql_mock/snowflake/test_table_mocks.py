import os

import pytest
from pydantic import ValidationError

from sql_mock.snowflake.column_mocks import INTEGER
from sql_mock.snowflake.table_mocks import SnowflakeMockTable
from sql_mock.table_mocks import table_meta


@table_meta(table_ref="mock_test_table")
class MockTestTable(SnowflakeMockTable):
    id = INTEGER(default=1)


@pytest.fixture(autouse=True)
def patch_os_environment_variables(mocker):
    mocker.patch.dict(
        os.environ,
        {
            "SQL_MOCK_SNOWFLAKE_ACCOUNT": "account",
            "SQL_MOCK_SNOWFLAKE_USER": "user",
            "SQL_MOCK_SNOWFLAKE_PASSWORD": "password",
        },
        clear=True,
    )


def test_init_with_environment_variables(mocker):
    """...then the env vars should be used to set the attributes"""
    table = MockTestTable()
    assert table.settings.account == "account"
    assert table.settings.user == "user"
    assert table.settings.password == "password"


def test_init_with_missing_configs(mocker):
    """...then it should raise an error"""
    mocker.patch.dict(
        os.environ,
        {},
        clear=True,
    )
    with pytest.raises(ValidationError):
        MockTestTable()


def test_get_results(mocker):
    """Test the _get_results method."""
    # Create a mock query job result
    mock_query_job_result = [
        {"column1": "value1", "column2": "value2"},
        {"column1": "value3", "column2": "value4"}
        # Add more rows as needed
    ]
    query = "SELECT 1, 2"
    # Mock the Snowflake connector
    mock_connect = mocker.patch("sql_mock.snowflake.table_mocks.connect")
    mock_cursor = mock_connect.return_value.__enter__.return_value.cursor
    mock_execute = mock_cursor.return_value.__enter__.return_value.execute
    mock_fetchall = mock_cursor.return_value.__enter__.return_value.fetchall
    mock_fetchall.return_value = mock_query_job_result

    instance = SnowflakeMockTable()
    result = instance._get_results(query=query)

    assert result == mock_query_job_result
    mock_execute.assert_called_once_with(query)
